from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, request, session
from flask import redirect, url_for, render_template, jsonify, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.exceptions import HTTPException

from . import db, cache, providers
from .models import User, Account, Resume, Task, ResumeSchema
from .providers import ProviderError


views = Blueprint('views', __name__)


@cache.cached(timeout=300)
def system_info():
    limit = current_app.config['TASKS_LIMIT']
    info = dict(
        version=current_app.version, providers=[], users=User.query.count(),
        accounts=Account.query.count(), resume=Resume.query.count(),
        tasks=Task.query.order_by(Task.finished_at.desc()).limit(limit).all())

    resume_join = Resume.query.join(Account)
    for p in providers.keys():
        info['providers'].append(dict(
            name=p, accounts=Account.query.filter_by(provider=p).count(),
            resume=resume_join.filter(Account.provider == p).count()))

    return info


@views.app_template_filter('isoformat')
def isoformat_with_timezone(date):
    return date.replace(tzinfo=timezone.utc).isoformat()


@views.app_errorhandler(HTTPException)
def error_page(err):
    return render_template('error.html', error=err), err.code


@views.route('/', methods=['GET'])
def main():
    return render_template('main.html', info=system_info())


@views.route('/auth/<provider>', methods=['GET'])
def login(provider):
    provider = providers.get(provider.lower())
    if not provider:
        flash('Invalid provider', 'error')
        return redirect(url_for('views.main'))

    code = request.args.get('code')
    if not code:
        return redirect(provider.redirect_url)

    try:
        ids = provider.tokenize(code, refresh=False)
        identity = provider.identity(ids['access_token'])
    except ProviderError as e:
        current_app.logger.warning(f'Auth failed: {e}')
        flash('Provider error: auth failed', 'error')
        return redirect(url_for('views.main'))

    account = Account.query.filter_by(
        identity=identity, provider=provider.name).first()

    if current_user.is_authenticated:
        user = current_user
    else:
        user = None

    if (account) and (user):
        account.user = user
    elif (account) and (not user):
        user = account.user
    else:
        if not user:
            user = User()
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f'User created: {user}')
        account = Account(identity=identity, user=user, provider=provider.name)
        current_app.logger.info(f'Account created: {account}')
        flash(f'New account created - {identity}', 'info')

    account.access = ids['access_token']
    account.refresh = ids['refresh_token']
    account.expires = datetime.utcnow() + timedelta(seconds=ids['expires_in'])

    current_app.logger.info(f'Account login: {account}')

    db.session.add(user, account)
    db.session.commit()

    if current_user.is_anonymous:
        login_user(user)

    session['last_provider'] = provider.name
    cache.clear()

    return redirect(url_for('views.resume'))


@views.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    session.pop('_flashes', None)
    return redirect(url_for('views.main'))


@views.route('/accounts', methods=['GET'])
@login_required
def accounts():
    return render_template('accounts.html')


@views.route('/resume', methods=['GET'])
@login_required
def resume():
    user_resume = list()
    schema = ResumeSchema()

    for account in current_user.accounts:
        if account.provider not in providers:  # pragma: no cover
            flash(f'Provider unavailable: {account.provider.upper()}', 'error')
            continue

        try:
            account_resume = providers[account.provider].fetch(account.access)
        except ProviderError as e:
            current_app.logger.error(f'Fetch failed: {account}, code={e}')
            flash(f'Invalid account - {account.identity}', 'error')
            continue

        new_account_resume = []
        resume_ids = [i['identity'] for i in account_resume]
        resumes = Resume.query.filter(Resume.identity.in_(resume_ids)).all()

        for acc_resume in account_resume:
            inst = {i.identity: i for i in resumes}.get(acc_resume['identity'])
            resume = schema.load(acc_resume, session=db.session, instance=inst)
            resume.account = account
            new_account_resume.append(resume)
            user_resume.append({**schema.dump(resume), **acc_resume})

        account.resume = new_account_resume

    db.session.commit()

    return render_template('resume.html', resumes=user_resume)


@views.route('/resume', methods=['POST'])
@login_required
def switch():
    resume_id = request.form.get('resume')
    if not resume_id:
        current_app.logger.warning('Resume id is not provided')
        return jsonify('Invalid resume identity'), 400

    current_acc_ids = [acc.identity for acc in current_user.accounts]
    resume = Resume.query.filter_by(identity=resume_id).filter(
        Resume.account_id.in_(current_acc_ids)).first_or_404()

    resume.autoupdate = (not resume.autoupdate)
    current_state = resume.autoupdate

    current_app.logger.info(f'Switch success: {resume}')

    db.session.add(resume)
    db.session.commit()

    return jsonify(state=current_state)
