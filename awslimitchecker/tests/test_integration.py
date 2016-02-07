"""
awslimitchecker/tests/test_integration.py

The latest version of this package is available at:
<https://github.com/jantman/awslimitchecker>

################################################################################
Copyright 2015 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of awslimitchecker, also known as awslimitchecker.

    awslimitchecker is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    awslimitchecker is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with awslimitchecker.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/awslimitchecker> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

import pytest
import os
import logging
from awslimitchecker.utils import dict2cols
from awslimitchecker.limit import SOURCE_TA, SOURCE_API
from awslimitchecker.checker import AwsLimitChecker
from awslimitchecker.services import _services
from awslimitchecker.connectable import Connectable

REGION = 'us-west-2'


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get('TRAVIS_PULL_REQUEST', None) != 'false',
    reason='Not running integration tests for pull request'
)
class TestIntegration(object):
    """
    !!!!!!IMPORTANT NOTE!!!!!!!

    Using pytest 2.8.7, it appears that module- or class-level markers don't
    get transferred to tests that are run via ``yield``. The only sufficient
    way I've found to get the desired behavior is to apply the
    ``@pytest.mark.integration`` marker to every test-related function directly.
    """

    def setup(self):
        # setup debug-level logging for awslimitchecker
        logger = logging.getLogger("awslimitchecker")
        FORMAT = "[%(levelname)s %(filename)s:%(lineno)s - " \
            "%(name)s.%(funcName)s() ] %(message)s"
        debug_formatter = logging.Formatter(fmt=FORMAT)
        for h in logger.handlers:
            h.setFormatter(debug_formatter)
        logger.setLevel(logging.DEBUG)
        # capture the AWS-related env vars

    @pytest.mark.integration
    def verify_limits(self, checker_args, creds, service_name, use_ta,
                      expect_api_source):
        """
        This essentially replicates what's done when awslimitchecker is called
        from the command line with ``-l``. This replicates some of the internal
        logic of :py:class:`~awslimitchecker.runner.Runner`.

        The main purpose is:

        1. to allow passing in an existing
           :py:class:`awslimitchecker.checker.Checker` instance for testing
           the various authentication options, and,
        2. to verify that at least some limits are found

        This method is largely a duplication of
        :py:meth:`~awslimitchecker.runner.Runner.list_limits`.

        :param checker_args: dict of kwargs to pass to
          :py:class:`awslimitchecker.checker.Checker` constructor
        :type checker_args: dict
        :param creds: AWS access key ID and secret key
        :type creds: tuple
        :param service_name: the Service name to test limits for; if None,
            check for all.
        :type service_name: str
        :param use_ta: whether or not to use TrustedAdvisor
        :type use_ta: bool
        :param expect_api_source: whether or not to expect a limit with an
          API source
        :type expect_api_source: bool
        """
        Connectable.credentials = None
        os.environ['AWS_ACCESS_KEY_ID'] = creds[0]
        os.environ['AWS_SECRET_ACCESS_KEY'] = creds[1]

        checker = AwsLimitChecker(**checker_args)
        limits = checker.get_limits(use_ta=use_ta, service=service_name)

        have_api_source = False
        data = {}
        for svc in sorted(limits.keys()):
            for lim in sorted(limits[svc].keys()):
                src_str = ''
                if limits[svc][lim].get_limit_source() == SOURCE_API:
                    have_api_source = True
                    src_str = ' (API)'
                if limits[svc][lim].get_limit_source() == SOURCE_TA:
                    src_str = ' (TA)'
                data["{s}/{l}".format(s=svc, l=lim)] = '{v}{t}'.format(
                    v=limits[svc][lim].get_limit(),
                    t=src_str)
        # this is the normal Runner output
        print(dict2cols(data))
        if expect_api_source:
            assert have_api_source is True

    @pytest.mark.integration
    def verify_usage(self, checker_args, creds, service_name, expect_usage):
        """
        This essentially replicates what's done when awslimitchecker is called
        from the command line with ``-u``. This replicates some of the internal
        logic of :py:class:`~awslimitchecker.runner.Runner`.

        The main purpose is:

        1. to allow passing in an existing
           :py:class:`awslimitchecker.checker.Checker` instance for testing
           the various authentication options, and,
        2. to verify that at least some usage is found

        This method is largely a duplication of
        :py:meth:`~awslimitchecker.runner.Runner.show_usage`.

        :param checker_args: dict of kwargs to pass to
          :py:class:`awslimitchecker.checker.Checker` constructor
        :type checker_args: dict
        :param creds: AWS access key ID and secret key
        :type creds: tuple
        :param service_name: the Service name to test usage for; if None,
            check for all.
        :type service_name: str
        :param expect_usage: whether or not to expect non-zero usage
        :type expect_usage: bool
        """
        Connectable.credentials = None
        os.environ['AWS_ACCESS_KEY_ID'] = creds[0]
        os.environ['AWS_SECRET_ACCESS_KEY'] = creds[1]

        checker = AwsLimitChecker(**checker_args)
        checker.find_usage(service=service_name)
        limits = checker.get_limits(service=service_name)
        have_usage = False
        data = {}
        for svc in sorted(limits.keys()):
            for lim in sorted(limits[svc].keys()):
                limit = limits[svc][lim]
                data["{s}/{l}".format(s=svc, l=lim)] = '{v}'.format(
                    v=limit.get_current_usage_str())
                for usage in limit.get_current_usage():
                    if usage.get_value() != 0:
                        have_usage = True
        # this is the normal Runner command line output
        print(dict2cols(data))
        if expect_usage:
            assert have_usage is True

    @pytest.mark.integration
    def DONOTtest_default_creds_all_services(self):
        """Test running alc with all services enabled"""
        creds = self.normal_creds()
        checker_args = {'region': REGION}
        yield "limits", self.verify_limits, checker_args, \
              creds, None, True, True
        yield "usage", self.verify_usage, checker_args, creds, None, True

    @pytest.mark.integration
    def DONOTtest_default_creds_each_service(self):
        """test running one service at a time for all services"""
        creds = self.normal_creds()
        checker_args = {'region': REGION}
        for sname in _services:
            eu = False
            if sname in ['RDS', 'VPC', 'EC2', 'ElastiCache', 'EBS']:
                eu = True
            yield "%s limits" % sname, self.verify_limits, checker_args, \
                  creds, sname, True, False
            yield "%s usage" % sname, self.verify_usage, checker_args, \
                  creds, sname, eu

    ###########################################################################
    # STS tests
    # Since connection logic is shared by all service classes and
    # TrustedAdvisor, just running a single service should suffice to test for
    # STS functionality.
    # As of 0.3.0, VPC seems to be the fastest service to query, so we'll use
    # that. In reality, all we care about in these further (STS) tests are that
    # we can connect and auth.
    ###########################################################################

    @pytest.mark.integration
    def test_sts(self):
        """test normal STS role"""
        creds = self.sts_creds()
        checker_args = {
            'account_id': os.environ.get('AWS_MASTER_ACCOUNT_ID', None),
            'account_role': 'alc-integration-sts',
            'region': REGION,
        }
        yield "VPC limits", self.verify_limits, checker_args, creds, \
              'VPC', True, False
        yield "VPC usage", self.verify_usage, checker_args, creds, 'VPC', True

    @pytest.mark.integration
    def test_sts_external_id(self):
        """test STS role with external ID"""
        creds = self.sts_creds()
        checker_args = {
            'account_id': os.environ.get('AWS_MASTER_ACCOUNT_ID', None),
            'account_role': 'alc-integration-sts',
            'region': REGION,
            'external_id': os.environ.get('AWS_EXTERNAL_ID', None),
        }
        yield "VPC limits", self.verify_limits, checker_args, creds, \
              'VPC', True, False
        yield "VPC usage", self.verify_usage, checker_args, creds, 'VPC', True

    @pytest.mark.integration
    def DONOTtest_sts_mfa(self):
        """test STS role with MFA"""
        creds = self.sts_creds()
        checker_args = {
            'account_id': os.environ.get('AWS_MASTER_ACCOUNT_ID', None),
            'account_role': 'alc-integration-sts',
            'region': REGION,
            'external_id': os.environ.get('AWS_EXTERNAL_ID', None),
            'mfa_serial_number': '',
            'mfa_token': ''
        }
        yield "VPC limits", self.verify_limits, checker_args, creds, \
              'VPC', True, False
        yield "VPC usage", self.verify_usage, checker_args, creds, 'VPC', True

    def normal_creds(self):
        return (
            os.environ.get('AWS_MAIN_ACCESS_KEY_ID', None),
            os.environ.get('AWS_MAIN_SECRET_ACCESS_KEY', None)
        )

    def sts_creds(self):
        return (
            os.environ.get('AWS_INTEGRATION_ACCESS_KEY_ID', None),
            os.environ.get('AWS_INTEGRATION_SECRET_KEY', None)
        )
