from functools import wraps
from time import sleep
from datetime import datetime, timedelta

from flask import current_app
from celery import current_task
from celery.utils.log import get_task_logger

from . import db, celery, providers
from .models import User, Account, Resume, Task
from .providers import ProviderError


logger = get_task_logger(__name__)


def resultify_task(func):
    @wraps(func)
    def resultify(*args, **kwargs):
        started = datetime.utcnow()
        result = func(*args, **kwargs)
        task = Task(
            identity=current_task.request.id, name=func.__name__,
            started_at=started, finished_at=datetime.utcnow(),
            success=result['success'], skipped=result['skipped'],
            total=result['total'])
        db.session.add(task)
        db.session.commit()
        return result
    return resultify


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        current_app.config['TOUCH_INTERVAL'], touch_resume.s())
    sender.add_periodic_task(
        current_app.config['REAUTH_INTERVAL'], refresh_tokens.s())
    sender.add_periodic_task(
        current_app.config['CLEANUP_TASKS_INTERVAL'], cleanup_tasks.s())
    sender.add_periodic_task(
        current_app.config['CLEANUP_RESUME_INTERVAL'], cleanup_resume.s())
    sender.add_periodic_task(
        current_app.config['CLEANUP_ACCOUNTS_INTERVAL'], cleanup_accounts.s())
    sender.add_periodic_task(
        current_app.config['CLEANUP_USERS_INTERVAL'], cleanup_users.s())


@celery.task
@resultify_task
def touch_resume():
    result = dict(total=0, success=0, skipped=0)
    resumes = Resume.query.filter_by(autoupdate=True).all()
    for resume in [r for r in resumes if r.account.provider in providers]:
        sleep(0.3)
        try:
            provider = providers[resume.account.provider]
            if resume.updelta < provider.touch_limit:
                result['skipped'] += 1
                logger.debug(f'Touch resume limit skip: {resume}')
                continue
            provider.touch(token=resume.account.access, resume=resume.identity)
            resume.published = datetime.utcnow()
        except ProviderError as e:
            result['skipped'] += 1
            logger.warning(f'Resume autoupdate disabled: {resume}, {e}')
            resume.autoupdate = False
        except Exception as e:  # pragma: no cover
            result['skipped'] += 1
            logger.exception(f'Touch resume error: {resume}, err={e}')
        else:
            result['success'] += 1
            logger.info(f'Touch resume success: {resume}')
        finally:
            result['total'] += 1
            db.session.commit()

    return result


@celery.task
def refresh_tokens():
    result = dict(total=0, success=0, skipped=0)
    accounts = Account.query.all()
    for account in [acc for acc in accounts if acc.provider in providers]:
        sleep(0.3)
        try:
            provider = providers[account.provider]
            ids = provider.tokenize(account.refresh, refresh=True)

            account.access = ids['access_token']
            account.refresh = ids['refresh_token']

            delta = timedelta(seconds=ids['expires_in'])
            account.expires = datetime.utcnow() + delta

            db.session.add(account)
            db.session.commit()
        except ProviderError as e:  # pragma: no cover
            result['skipped'] += 1
            logger.warning(f'Refresh token skip: {account}, status={e}')
        except Exception as e:  # pragma: no cover
            result['skipped'] += 1
            logger.exception(f'Refresh token error: {account}, err={e}')
        else:
            result['success'] += 1
            logger.info(f'Refresh token success: {account}')
        finally:
            result['total'] += 1

    return result


@celery.task
def cleanup_tasks():
    result = dict(total=0, success=0, skipped=0)
    tasks = Task.query.order_by('finished_at').all()
    for task in tasks[:-current_app.config['TASKS_LIMIT']]:
        logger.info(f'Cleanup task: {task}')
        try:
            db.session.delete(task)
            db.session.commit()
        except Exception as e:  # pragma: no cover
            result['skipped'] += 1
            logger.exception(f'Cleanup task skip: {task}, err={e}')
        else:
            result['success'] += 1
        finally:
            result['total'] += 1

    return result


@celery.task
def cleanup_resume():
    result = dict(total=0, success=0, skipped=0)
    resumes = Resume.query.filter_by(autoupdate=False).all()
    for resume in resumes:
        logger.info(f'Cleanup resume: {resume}')
        try:
            db.session.delete(resume)
            db.session.commit()
        except Exception as e:  # pragma: no cover
            result['skipped'] += 1
            logger.exception(f'Cleanup resume skip: {resume}, err={e}')
        else:
            result['success'] += 1
        finally:
            result['total'] += 1

    return result


@celery.task
def cleanup_accounts():
    result = dict(total=0, success=0, skipped=0)
    accounts = Account.query.filter(~Account.resume.any()).all()
    for account in accounts:
        logger.info(f'Cleanup account: {account}')
        try:
            db.session.delete(account)
            db.session.commit()
        except Exception as e:  # pragma: no cover
            result['skipped'] += 1
            logger.exception(f'Cleanup account skip: {account}, err={e}')
        else:
            result['success'] += 1
        finally:
            result['total'] += 1

    return result


@celery.task
def cleanup_users():
    result = dict(total=0, success=0, skipped=0)
    users = User.query.filter(~User.accounts.any()).all()
    for user in users:
        logger.info(f'Cleanup user: {user}')
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:  # pragma: no cover
            result['skipped'] += 1
            logger.exception(f'Cleanup user skip: {user}, err={e}')
        else:
            result['success'] += 1
        finally:
            result['total'] += 1

    return result
