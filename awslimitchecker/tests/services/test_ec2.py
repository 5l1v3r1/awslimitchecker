"""
awslimitchecker/tests/services/test_ec2.py

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
bugs please submit them at <https://github.com/jantman/pydnstest> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

from mock import Mock, patch, call
from contextlib import nested
from boto.ec2.connection import EC2Connection
from boto.ec2.instance import Instance, Reservation
from awslimitchecker.services.ec2 import _Ec2Service
from awslimitchecker.limit import _AwsLimit


class Test_Ec2Service(object):

    def test_init(self):
        """test __init__()"""
        cls = _Ec2Service()
        assert cls.service_name == 'EC2'
        assert cls.conn is None

    def test_connect(self):
        """test connect()"""
        mock_conn = Mock()
        cls = _Ec2Service()
        with patch('awslimitchecker.services.ec2.boto.connect_ec2') as mock_ec2:
            mock_ec2.return_value = mock_conn
            cls.connect()
        assert mock_ec2.mock_calls == [call()]
        assert mock_conn.mock_calls == []

    def test_connect_again(self):
        """make sure we re-use the connection"""
        mock_conn = Mock()
        cls = _Ec2Service()
        cls.conn = mock_conn
        with patch('awslimitchecker.services.ec2.boto.connect_ec2') as mock_ec2:
            mock_ec2.return_value = mock_conn
            cls.connect()
        assert mock_ec2.mock_calls == []
        assert mock_conn.mock_calls == []

    def test_instance_types(self):
        cls = _Ec2Service()
        types = cls._instance_types()
        assert len(types) == 47
        assert 't2.micro' in types
        assert 'r3.8xlarge' in types
        assert 'c3.large' in types
        assert 'i2.4xlarge' in types
        assert 'd2.2xlarge' in types
        assert 'g2.8xlarge' in types
        assert 'hs1.8xlarge' in types
        assert 'cg1.4xlarge' in types

    def test_get_limits(self):
        cls = _Ec2Service()
        init_limits = cls.limits
        limits = cls.get_limits()
        assert limits == init_limits
        assert len(limits) == 47
        for x in limits:
            assert isinstance(limits[x], _AwsLimit)
            assert limits[x].service_name == 'EC2'
        # check a random subset of limits
        t2_micro = limits['Running On-Demand t2.micro Instances']
        assert t2_micro.default_limit == 20
        assert t2_micro.limit_type == 'On-Demand Instances'
        assert t2_micro.limit_subtype == 't2.micro'
        c4_8xlarge = limits['Running On-Demand c4.8xlarge Instances']
        assert c4_8xlarge.default_limit == 5
        assert c4_8xlarge.limit_type == 'On-Demand Instances'
        assert c4_8xlarge.limit_subtype == 'c4.8xlarge'
        i2_8xlarge = limits['Running On-Demand i2.8xlarge Instances']
        assert i2_8xlarge.default_limit == 2
        assert i2_8xlarge.limit_type == 'On-Demand Instances'
        assert i2_8xlarge.limit_subtype == 'i2.8xlarge'

    def test_find_usage(self):
        pb = 'awslimitchecker.services.ec2._Ec2Service'  # patch base path
        with nested(
                patch('%s.connect' % pb, autospec=True),
                patch('%s._find_usage_instances' % pb, autospec=True),
        ) as (
            mock_connect,
            mock_instances,
        ):
            cls = _Ec2Service()
            cls.find_usage()
        assert mock_connect.mock_calls == [call(cls)]
        assert mock_instances.mock_calls == [call(cls)]

    def test_find_usage_instances(self):
        mock_t2_micro = Mock(spec_set=_AwsLimit)
        mock_r3_2xlarge = Mock(spec_set=_AwsLimit)
        mock_c4_4xlarge = Mock(spec_set=_AwsLimit)
        limits = {
            'Running On-Demand t2.micro Instances': mock_t2_micro,
            'Running On-Demand r3.2xlarge Instances': mock_r3_2xlarge,
            'Running On-Demand c4.4xlarge Instances': mock_c4_4xlarge,
        }

        cls = _Ec2Service()
        mock_inst1A = Mock(spec_set=Instance)
        type(mock_inst1A).id = '1A'
        type(mock_inst1A).instance_type = 't2.micro'
        type(mock_inst1A).spot_instance_request_id = None

        mock_inst1B = Mock(spec_set=Instance)
        type(mock_inst1B).id = '1B'
        type(mock_inst1B).instance_type = 'r3.2xlarge'
        type(mock_inst1B).spot_instance_request_id = None

        mock_res1 = Mock(spec_set=Reservation)
        type(mock_res1).instances = [mock_inst1A, mock_inst1B]

        mock_inst2A = Mock(spec_set=Instance)
        type(mock_inst2A).id = '2A'
        type(mock_inst2A).instance_type = 'c4.4xlarge'
        type(mock_inst2A).spot_instance_request_id = None

        mock_inst2B = Mock(spec_set=Instance)
        type(mock_inst2B).id = '2B'
        type(mock_inst2B).instance_type = 't2.micro'
        type(mock_inst2B).spot_instance_request_id = '1234'

        mock_res2 = Mock(spec_set=Reservation)
        type(mock_res2).instances = [mock_inst2A, mock_inst2B]

        mock_conn = Mock(spec_set=EC2Connection)
        mock_conn.get_all_reservations.return_value = [
            mock_res1,
            mock_res2
        ]
        cls.conn = mock_conn
        cls.limits = limits
        with patch('awslimitchecker.services.ec2._Ec2Service._instance_types',
                   autospec=True) as mock_itypes:
            mock_itypes.return_value = [
                't2.micro',
                'r3.2xlarge',
                'c4.4xlarge',
            ]
            cls._find_usage_instances()
        assert mock_t2_micro.mock_calls == [call._set_current_usage(1)]
        assert mock_r3_2xlarge.mock_calls == [call._set_current_usage(1)]
        assert mock_c4_4xlarge.mock_calls == [call._set_current_usage(1)]

    def test_find_usage_instances_key_error(self):
        mock_inst1A = Mock(spec_set=Instance)
        type(mock_inst1A).id = '1A'
        type(mock_inst1A).instance_type = 'foobar'
        type(mock_inst1A).spot_instance_request_id = None
        mock_res1 = Mock(spec_set=Reservation)
        type(mock_res1).instances = [mock_inst1A]

        mock_conn = Mock(spec_set=EC2Connection)
        mock_conn.get_all_reservations.return_value = [mock_res1]
        cls = _Ec2Service()
        cls.conn = mock_conn
        cls.limits = {'Running On-Demand t2.micro Instances': Mock()}
        with patch('awslimitchecker.services.ec2._Ec2Service._instance_types',
                   autospec=True) as mock_itypes:
            mock_itypes.return_value = ['t2.micro']
            with patch('awslimitchecker.services.ec2.logger') as mock_logger:
                cls._find_usage_instances()
        assert mock_logger.mock_calls == [
            call.error("ERROR - unknown instance type 'foobar'; not counting"),
        ]
