# Special thanks to Hynek Schlawack for providing excellent documentation:
#
# https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/

import os
from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='keyholer',
    version='0.7.0',
    description='Simple SSH key management for shell servers',
    long_description=(read('README.rst') + '\n\n' +
                      read('AUTHORS.rst') + '\n\n' +
                      read('CHANGELOG.rst')),
    url='http://zwhite.github.io/keyholer',
    license='MIT',
    author='Zach White',
    author_email='zwhite@darkstar.frop.org',
    install_requires=['flask', 'twilio'],
    packages=find_packages(),
    scripts=['keyholerd'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: BSD :: NetBSD',
        'Operating System :: POSIX :: BSD :: OpenBSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: System',
        'Topic :: System :: Recovery Tools',
        'Topic :: System :: Systems Administration',
    ],
)
