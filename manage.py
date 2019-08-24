#!/usr/bin/env python

import os
import re
import unittest

from git import Repo
from semver import match
from click import option, argument, echo, ClickException

from touchresume.cli import cli
from touchresume import __version__


@cli.command(with_appcontext=False)
@option('-d', '--dir', default='tests', help='Directory with tests')
def test(dir):
    """Discover and run unit tests."""
    testsuite = unittest.TestLoader().discover(dir)
    unittest.TextTestRunner(verbosity=2, buffer=True).run(testsuite)


@cli.command(with_appcontext=False)
@option('-d', '--dev', default='dev', help='Develop branch (dev)')
@option('-m', '--master', default='master', help='Master branch (master)')
@argument('version')
def release(dev, master, version, app_path='touchresume'):
    """Make Git release."""
    if not match(version, f'>{__version__}'):
        raise ClickException(f'Version must be greater than {__version__}')

    repo = Repo()
    release = f'release/{version}'

    echo(f'Create {release} branch')
    repo.head.ref = repo.heads[dev]
    repo.head.ref = repo.create_head(release)

    echo(f'Bump version - {version}')
    version_file = os.path.join(app_path, '__init__.py')
    with open(version_file, 'r+') as f:
        content = f.read()
        target = f"__version__ = '{__version__}'"
        value = f"__version__ = '{version}'"
        f.seek(0)
        f.write(content.replace(target, value))
    repo.index.add([version_file])
    repo.index.commit(f'bump version - v{version}')

    diff = repo.head.commit.diff(None)

    cf = re.compile(r'^change[s|log].*')
    changelog_files = [d.a_path for d in diff if cf.match(d.a_path.lower())]
    if changelog_files:
        echo(f'Commit {", ".join(changelog_files)}')
        repo.index.add(changelog_files)
        repo.index.commit(f'update changelog - v{version}')

    rf = 'readme'
    readme_files = [d.a_path for d in diff if d.a_path.lower().startswith(rf)]
    if readme_files:
        echo(f'Commit {", ".join(readme_files)}')
        repo.index.add(readme_files)
        repo.index.commit(f'update readme - v{version}')

    echo(f'Merge {release} into {master}')
    repo.head.ref = repo.heads[master]
    parents = (repo.branches[release].commit, repo.branches[master].commit)
    repo.index.commit(f'merge {release}', parent_commits=parents)

    echo(f'Create v{version} tag')
    repo.create_tag(f'v{version}')

    echo(f'Merge {release} back into {dev}')
    repo.head.ref = repo.heads[dev]
    dev_parents = (repo.branches[release].commit, repo.branches[dev].commit)
    repo.index.commit(f'merge {release} back', parent_commits=dev_parents)

    echo(f'Delete {release} branch')
    repo.delete_head(release)


if __name__ == '__main__':
    cli()
