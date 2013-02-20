"""
Flask-Reloaded
-------------

A kinda ghetto way to reload your Flask page when *any* file (templates, css,
js, etc).
"""
from setuptools import setup


setup(
    name='Flask-Reloaded',
    version='1.0',
    url='',
    license='BSD',
    author='Nicholas Bollweg',
    author_email='nicholas.bollweg@gtri.gatech.edu',
    description='Refresh your browser when you change CSS, JS, templates.',
    long_description=open('README.md', 'r').read(),
    packages=['flask_reloaded'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.8'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
