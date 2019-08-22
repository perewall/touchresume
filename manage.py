#!/usr/bin/env python

from click import option

from touchresume.cli import cli


@cli.command(with_appcontext=False)
@option('-d', '--dir', default='tests', help='Directory with tests')
def test(dir):
    """Discover and run unit tests."""
    from unittest import TestLoader, TextTestRunner
    testsuite = TestLoader().discover(dir)
    TextTestRunner(verbosity=2, buffer=True).run(testsuite)


if __name__ == '__main__':
    cli()
