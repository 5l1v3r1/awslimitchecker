"""
setup.py

The latest version of this package is available at:
<https://github.com/jantman/boto-limit-checker>

##################################################################################
Copyright 2015 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of botolimitchecker, also known as boto-limit-checker.

    botolimitchecker is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    botolimitchecker is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with botolimitchecker.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
##################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/pydnstest> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
##################################################################################
"""

from setuptools import setup
from sys import version_info
from botolimitchecker.version import VERSION, PROJECT_URL

# boto isn't py3-compatible yet
if version_info[0] > 2 or version_info[1] < 6:
    raise SystemExit("ERROR - boto currently requires python 2.6 or 2.7;"
                     " once boto announces py3 compatibility, "
                     "botolimitchecker will too")

with open('README.rst') as file:
    long_description = file.read()

requires = [
    'boto>=2.0',
]

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Internet',
    'Topic :: System :: Monitoring',
]

setup(
    name='botolimitchecker',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=['botolimitchecker', 'botolimitchecker.tests'],
    entry_points="""
    [console_scripts]
    botolimitchecker = botolimitchecker.runner:console_entry_point
    """,
    url=PROJECT_URL,
    description='A script and python module to check your AWS service limits and usage using boto.',
    long_description=long_description,
    install_requires=requires,
    keywords="AWS EC2 Amazon boto limits cloud",
    classifiers=classifiers
)
