"""
awslimitchecker/quotas.py

The latest version of this package is available at:
<https://github.com/jantman/awslimitchecker>

##############################################################################
Copyright 2015-2019 Jason Antman <jason@jasonantman.com>

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
##############################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/awslimitchecker> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##############################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
##############################################################################
"""

import logging

from awslimitchecker.connectable import Connectable

logger = logging.getLogger(__name__)


class ServiceQuotasClient(Connectable):
    """
    Client for the AWS Service Quotas service, that manages retrieving quotas
    information and updating :py:class:`~.AwsLimit` instances for them. This
    class is also intended to cache Service Quotas responses.
    """

    api_name = 'service-quotas'

    def __init__(self, boto_connection_kwargs):
        """
        should only **ever** be called from :py:meth:`~.get_instance`.

        :param boto_connection_kwargs: keyword arguments to pass to boto3
          connection methods.
        :type boto_connection_kwargs: dict
        """
        self._boto3_connection_kwargs = boto_connection_kwargs
        self._cache = {}
        self.conn = None

    def quotas_for_service(self, service_code):
        """
        Return this account's current quotas for the specified service code.
        Also cache them on this class instance.

        :param service_code: the service code to get quotas for
        :type service_code: str
        :return: QuotaName to dictionary of quota information returned by the
          service
        :rtype: dict
        """
        if service_code in self._cache:
            logger.debug(
                'Using cached quotas for service code: %s', service_code
            )
            return self._cache[service_code]
        self.connect()
        logger.debug(
            'Getting service quotas for service code: %s', service_code
        )
        self._cache[service_code] = {}
        paginator = self.conn.get_paginator('list_service_quotas')
        for page in paginator.paginate(ServiceCode=service_code):
            for item in page['Quotas']:
                if item['QuotaName'] in self._cache[service_code]:
                    logger.error(
                        'ERROR: Received duplicate service quota for service '
                        'code %s quota name "%s" - QuotaCodes %s and %s',
                        service_code, item['QuotaName'],
                        self._cache[service_code][
                            item['QuotaName']
                        ]['QuotaCode'], item['QuotaCode']
                    )
                self._cache[service_code][item['QuotaName']] = item
        logger.debug(
            'Retrieved %d quotas for service code %s',
            len(self._cache[service_code]), service_code
        )
        return self._cache[service_code]

    def get_quota_value(self, service_code, quota_name, units='None'):
        """
        Return a given quota value, or None if it cannot be found. If
        ``units`` is a value other than ``None``, attempt to convert the value
        to the specified units.

        :param service_code: the service code to get a quota from
        :type service_code: str
        :param quota_name: the quota name to get
        :type quota_name: str
        :param units: the units for the value, or the string "None"
        :type units: str
        :return: the quota value
        :rtype: float or None
        :raises: UnknownQuotaUnitsException if the units cannot be converted
        """
        svc = self.quotas_for_service(service_code)
        if quota_name not in svc:
            return None
        if svc[quota_name]['Unit'] != 'None':
            raise NotImplementedError()
        return svc[quota_name]['Value']
