import io
import re

from setuptools import setup


with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()


with io.open('touchresume/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)


setup(
    name='TouchResume',
    version=version,
    url='https://github.com/perewall/touchresume',
    license='MIT',
    author='perewall',
    author_email='art@pwmedia.ru',
    description='Tool for automatically update your CV on some job boards',
    long_description=readme,
    long_description_content_type='text/markdown',
    platforms=['posix'],
    python_requires='>= 3.6',
    zip_safe=False,
    install_requires=[
        'flask >= 1.1.1',
        'flask_login >= 0.4.1',
        'flask_sqlalchemy >= 2.4.0',
        'flask_migrate >= 2.5.2',
        'flask_caching >= 1.7.2',
        'flask_cors >= 3.0.8',
        'flask_wtf >= 0.14.2',
        'flask_htmlmin >= 1.5.0',
        'flask_marshmallow >= 0.10.1',
        'flask_debugtoolbar >= 0.10.1',
        'marshmallow_sqlalchemy >= 0.17.0',
        'cerberus >= 1.3.1',
        'rauth >= 0.7.3',
        'redis >= 3.3.8',
        'celery >= 4.3.0',
        'celery_redbeat >= 0.13.0',
        'psycopg2_binary >= 2.8.3',
        'python_dotenv >= 0.10.3',
        'gunicorn[eventlet] >= 19.9.0',
        'sentry_sdk[flask] >= 0.11.1'
    ],
    entry_points={'console_scripts': ['touchresume = touchresume.cli:cli']},
    packages=['touchresume'],
    package_data={
        'touchresume': [
            'migrations/*',
            'migrations/versions/*',
            'providers/*',
            'templates/*'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
    ]
)
