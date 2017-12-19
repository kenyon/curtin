import mock

from curtin.block import iscsi
from .helpers import CiTestCase


class TestBlockIscsiPortalParsing(CiTestCase):

    def test_iscsi_portal_parsing_string(self):
        with self.assertRaisesRegexp(ValueError, 'not a string'):
            iscsi.assert_valid_iscsi_portal(1234)

    def test_iscsi_portal_parsing_no_port(self):
        # port must be specified
        with self.assertRaisesRegexp(ValueError, 'not in the format'):
            iscsi.assert_valid_iscsi_portal('192.168.1.12')
        with self.assertRaisesRegexp(ValueError, 'not in the format'):
            iscsi.assert_valid_iscsi_portal('fe80::a634:d9ff:fe40:768a')
        with self.assertRaisesRegexp(ValueError, 'not in the format'):
            iscsi.assert_valid_iscsi_portal('192.168.1.12:')
        with self.assertRaisesRegexp(ValueError, 'not in the format'):
            iscsi.assert_valid_iscsi_portal('test.example.com:')

    def test_iscsi_portal_parsing_valid_ip(self):
        # IP must be in [] for IPv6, if not we misparse
        host, port = iscsi.assert_valid_iscsi_portal(
            'fe80::a634:d9ff:fe40:768a:9999')
        self.assertEquals(host, 'fe80::a634:d9ff:fe40:768a')
        self.assertEquals(port, 9999)
        # IP must not be in [] if port is specified for IPv4
        with self.assertRaisesRegexp(ValueError, 'Invalid IPv6 address'):
            iscsi.assert_valid_iscsi_portal('[192.168.1.12]:9000')
        with self.assertRaisesRegexp(ValueError, 'Invalid IPv6 address'):
            iscsi.assert_valid_iscsi_portal('[test.example.com]:8000')

    def test_iscsi_portal_parsing_ip(self):
        with self.assertRaisesRegexp(ValueError, 'Invalid IPv6 address'):
            iscsi.assert_valid_iscsi_portal(
                '[1200::AB00:1234::2552:7777:1313]:9999')
        # cannot distinguish between bad IP and bad hostname
        host, port = iscsi.assert_valid_iscsi_portal('192.168:9000')
        self.assertEquals(host, '192.168')
        self.assertEquals(port, 9000)

    def test_iscsi_portal_parsing_port(self):
        with self.assertRaisesRegexp(ValueError, 'not in the format'):
            iscsi.assert_valid_iscsi_portal('192.168.1.12:ABCD')
        with self.assertRaisesRegexp(ValueError, 'not in the format'):
            iscsi.assert_valid_iscsi_portal('[fe80::a634:d9ff:fe40:768a]:ABCD')
        with self.assertRaisesRegexp(ValueError, 'not in the format'):
            iscsi.assert_valid_iscsi_portal('test.example.com:ABCD')

    def test_iscsi_portal_parsing_good_portals(self):
        host, port = iscsi.assert_valid_iscsi_portal('192.168.1.12:9000')
        self.assertEquals(host, '192.168.1.12')
        self.assertEquals(port, 9000)

        host, port = iscsi.assert_valid_iscsi_portal(
            '[fe80::a634:d9ff:fe40:768a]:9999')
        self.assertEquals(host, 'fe80::a634:d9ff:fe40:768a')
        self.assertEquals(port, 9999)

        host, port = iscsi.assert_valid_iscsi_portal('test.example.com:8000')
        self.assertEquals(host, 'test.example.com')
        self.assertEquals(port, 8000)

    # disk specification:
    # TARGETSPEC=host:proto:port:lun:targetname
    # root=iscsi:$TARGETSPEC
    # root=iscsi:user:password@$TARGETSPEC
    # root=iscsi:user:password:initiatoruser:initiatorpassword@$TARGETSPEC
    def test_iscsi_disk_basic(self):
        with self.assertRaisesRegexp(ValueError, 'must be specified'):
            iscsi.IscsiDisk('')

        # typo
        with self.assertRaisesRegexp(ValueError, 'must be specified'):
            iscsi.IscsiDisk('iscs:')

        # no specification
        with self.assertRaisesRegexp(ValueError, 'must be specified'):
            iscsi.IscsiDisk('iscsi:')
        with self.assertRaisesRegexp(ValueError, 'Both host and targetname'):
            iscsi.IscsiDisk('iscsi:::::')

    def test_iscsi_disk_ip_valid(self):
        # these are all misparses we cannot catch trivially
        i = iscsi.IscsiDisk('iscsi:192.168::::target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, '192.168')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 0)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:[fe80::]::::target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'fe80::')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 0)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:test.example::::target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'test.example')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 0)
        self.assertEquals(i.target, 'target')

    def test_iscsi_disk_port(self):
        with self.assertRaisesRegexp(ValueError, 'Specified iSCSI port'):
            iscsi.IscsiDisk('iscsi:192.168.1.12::ABCD::target')
        with self.assertRaisesRegexp(ValueError, 'Specified iSCSI port'):
            iscsi.IscsiDisk('iscsi:[fe80::a634:d9ff:fe40:768a:6]::ABCD::'
                            'target')
        with self.assertRaisesRegexp(ValueError, 'Specified iSCSI port'):
            iscsi.IscsiDisk('iscsi:test.example.com::ABCD::target')

    def test_iscsi_disk_target(self):
        with self.assertRaisesRegexp(ValueError, 'Both host and targetname'):
            iscsi.IscsiDisk('iscsi:192.168.1.12::::')
        with self.assertRaisesRegexp(ValueError, 'Both host and targetname'):
            iscsi.IscsiDisk('iscsi:[fe80::a634:d9ff:fe40:768a:6]::::')
        with self.assertRaisesRegexp(ValueError, 'Both host and targetname'):
            iscsi.IscsiDisk('iscsi:test.example.com::::')

    def test_iscsi_disk_ip(self):
        with self.assertRaisesRegexp(ValueError, 'Both host and targetname'):
            iscsi.IscsiDisk('iscsi:::::target')

    def test_iscsi_disk_auth(self):
        # user without password
        with self.assertRaises(ValueError):
            iscsi.IscsiDisk('iscsi:user@192.168.1.12::::target')
        with self.assertRaises(ValueError):
            iscsi.IscsiDisk('iscsi:user@[fe80::a634:d9ff:fe40:768a:6]::::'
                            'target')
        with self.assertRaises(ValueError):
            iscsi.IscsiDisk('iscsi:user@test.example.com::::target')

        # iuser without password
        with self.assertRaises(ValueError):
            iscsi.IscsiDisk('iscsi:user:password:iuser@192.168.1.12::::target')
        with self.assertRaises(ValueError):
            iscsi.IscsiDisk('iscsi:user:password:iuser@'
                            '[fe80::a634:d9ff:fe40:768a:6]::::target')
        with self.assertRaises(ValueError):
            iscsi.IscsiDisk(
                'iscsi:user:password:iuser@test.example.com::::target')

    def test_iscsi_disk_good_ipv4(self):
        i = iscsi.IscsiDisk('iscsi:192.168.1.12:6:3260:1:target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, '192.168.1.12')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:192.168.1.12::3260:1:target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, '192.168.1.12')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:192.168.1.12:::1:target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, '192.168.1.12')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:password@192.168.1.12:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, 'password')
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, '192.168.1.12')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:@192.168.1.12:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, '')
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, '192.168.1.12')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:password:iuser:ipassword@'
                            '192.168.1.12:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, 'password')
        self.assertEquals(i.iuser, 'iuser')
        self.assertEquals(i.ipassword, 'ipassword')
        self.assertEquals(i.host, '192.168.1.12')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:password:iuser:@'
                            '192.168.1.12:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, 'password')
        self.assertEquals(i.iuser, 'iuser')
        self.assertEquals(i.ipassword, '')
        self.assertEquals(i.host, '192.168.1.12')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user::iuser:@192.168.1.12:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, '')
        self.assertEquals(i.iuser, 'iuser')
        self.assertEquals(i.ipassword, '')
        self.assertEquals(i.host, '192.168.1.12')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

    def test_iscsi_disk_good_ipv6(self):
        i = iscsi.IscsiDisk(
            'iscsi:[fe80::a634:d9ff:fe40:768a:6]:5:3260:1:target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'fe80::a634:d9ff:fe40:768a:6')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk(
            'iscsi:[fe80::a634:d9ff:fe40:768a:6]::3260:1:target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'fe80::a634:d9ff:fe40:768a:6')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:[fe80::a634:d9ff:fe40:768a:6]:::1:target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'fe80::a634:d9ff:fe40:768a:6')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:password@'
                            '[fe80::a634:d9ff:fe40:768a:6]:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, 'password')
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'fe80::a634:d9ff:fe40:768a:6')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:@'
                            '[fe80::a634:d9ff:fe40:768a:6]:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, '')
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'fe80::a634:d9ff:fe40:768a:6')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:password:iuser:ipassword@'
                            '[fe80::a634:d9ff:fe40:768a:6]:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, 'password')
        self.assertEquals(i.iuser, 'iuser')
        self.assertEquals(i.ipassword, 'ipassword')
        self.assertEquals(i.host, 'fe80::a634:d9ff:fe40:768a:6')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:password:iuser:@'
                            '[fe80::a634:d9ff:fe40:768a:6]:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, 'password')
        self.assertEquals(i.iuser, 'iuser')
        self.assertEquals(i.ipassword, '')
        self.assertEquals(i.host, 'fe80::a634:d9ff:fe40:768a:6')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user::iuser:@'
                            '[fe80::a634:d9ff:fe40:768a:6]:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, '')
        self.assertEquals(i.iuser, 'iuser')
        self.assertEquals(i.ipassword, '')
        self.assertEquals(i.host, 'fe80::a634:d9ff:fe40:768a:6')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

    def test_iscsi_disk_good_hostname(self):
        i = iscsi.IscsiDisk('iscsi:test.example.com:6:3260:1:target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'test.example.com')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:test.example.com::3260:1:target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'test.example.com')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:test.example.com:::1:target')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'test.example.com')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:password@test.example.com:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, 'password')
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'test.example.com')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:@test.example.com:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, '')
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'test.example.com')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:password:iuser:ipassword@'
                            'test.example.com:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, 'password')
        self.assertEquals(i.iuser, 'iuser')
        self.assertEquals(i.ipassword, 'ipassword')
        self.assertEquals(i.host, 'test.example.com')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user:password:iuser:@'
                            'test.example.com:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, 'password')
        self.assertEquals(i.iuser, 'iuser')
        self.assertEquals(i.ipassword, '')
        self.assertEquals(i.host, 'test.example.com')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

        i = iscsi.IscsiDisk('iscsi:user::iuser:@test.example.com:::1:target')
        self.assertEquals(i.user, 'user')
        self.assertEquals(i.password, '')
        self.assertEquals(i.iuser, 'iuser')
        self.assertEquals(i.ipassword, '')
        self.assertEquals(i.host, 'test.example.com')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 1)
        self.assertEquals(i.target, 'target')

    # LP: #1679222
    def test_iscsi_target_parsing(self):
        i = iscsi.IscsiDisk(
            'iscsi:192.168.1.12::::iqn.2017-04.com.example.test:target-name')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, '192.168.1.12')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 0)
        self.assertEquals(i.target, 'iqn.2017-04.com.example.test:target-name')

        i = iscsi.IscsiDisk(
            'iscsi:[fe80::a634:d9ff:fe40:768a:6]::::'
            'iqn.2017-04.com.example.test:target-name')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'fe80::a634:d9ff:fe40:768a:6')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 0)
        self.assertEquals(i.target, 'iqn.2017-04.com.example.test:target-name')

        i = iscsi.IscsiDisk(
            'iscsi:test.example.com::::'
            'iqn.2017-04.com.example.test:target-name')
        self.assertEquals(i.user, None)
        self.assertEquals(i.password, None)
        self.assertEquals(i.iuser, None)
        self.assertEquals(i.ipassword, None)
        self.assertEquals(i.host, 'test.example.com')
        self.assertEquals(i.proto, '6')
        self.assertEquals(i.port, 3260)
        self.assertEquals(i.lun, 0)
        self.assertEquals(i.target, 'iqn.2017-04.com.example.test:target-name')


class TestBlockIscsiVolPath(CiTestCase):
    # non-iscsi backed disk returns false
    # regular iscsi-backed disk returns true
    # layered setup without an iscsi member returns false
    # layered setup with an iscsi member returns true

    def setUp(self):
        super(TestBlockIscsiVolPath, self).setUp()
        self.add_patch('curtin.block.iscsi.get_device_slave_knames',
                       'mock_get_device_slave_knames')
        self.add_patch('curtin.block.iscsi.path_to_kname',
                       'mock_path_to_kname')
        self.add_patch('curtin.block.iscsi.kname_is_iscsi',
                       'mock_kname_is_iscsi')

    def test_volpath_is_iscsi_false(self):
        volume_path = '/dev/wark'
        kname = 'wark'
        slaves = []
        self.mock_get_device_slave_knames.return_value = slaves
        self.mock_path_to_kname.return_value = kname
        self.mock_kname_is_iscsi.return_value = 'iscsi' in kname

        is_iscsi = iscsi.volpath_is_iscsi(volume_path)

        self.assertFalse(is_iscsi)
        self.mock_get_device_slave_knames.assert_called_with(volume_path)
        self.mock_path_to_kname.assert_called_with(volume_path)
        self.mock_kname_is_iscsi.assert_called_with(kname)

    def test_volpath_is_iscsi_true(self):
        volume_path = '/dev/wark'
        kname = 'wark-iscsi-lun-2'
        slaves = []
        self.mock_get_device_slave_knames.return_value = slaves
        self.mock_path_to_kname.return_value = kname
        self.mock_kname_is_iscsi.return_value = 'iscsi' in kname

        is_iscsi = iscsi.volpath_is_iscsi(volume_path)

        self.assertTrue(is_iscsi)
        self.mock_get_device_slave_knames.assert_called_with(volume_path)
        self.mock_path_to_kname.assert_called_with(volume_path)
        self.mock_kname_is_iscsi.assert_called_with(kname)

    def test_volpath_is_iscsi_layered_true(self):
        volume_path = '/dev/wark'
        slaves = ['wark', 'bzr', 'super-iscsi-lun-27']
        self.mock_get_device_slave_knames.return_value = slaves
        self.mock_path_to_kname.side_effect = lambda x: x
        self.mock_kname_is_iscsi.side_effect = lambda x: 'iscsi' in x

        is_iscsi = iscsi.volpath_is_iscsi(volume_path)

        self.assertTrue(is_iscsi)
        self.mock_get_device_slave_knames.assert_called_with(volume_path)
        self.mock_path_to_kname.assert_called_with(volume_path)
        self.mock_kname_is_iscsi.assert_has_calls([
            mock.call(x) for x in slaves])

    def test_volpath_is_iscsi_layered_false(self):
        volume_path = '/dev/wark'
        slaves = ['wark', 'bzr', 'nvmen27p47']
        self.mock_get_device_slave_knames.return_value = slaves
        self.mock_path_to_kname.side_effect = lambda x: x
        self.mock_kname_is_iscsi.side_effect = lambda x: 'iscsi' in x

        is_iscsi = iscsi.volpath_is_iscsi(volume_path)

        self.assertFalse(is_iscsi)
        self.mock_get_device_slave_knames.assert_called_with(volume_path)
        self.mock_path_to_kname.assert_called_with(volume_path)
        self.mock_kname_is_iscsi.assert_has_calls([
            mock.call(x) for x in slaves])

    def test_volpath_is_iscsi_missing_param(self):
        with self.assertRaises(ValueError):
            iscsi.volpath_is_iscsi(None)

# vi: ts=4 expandtab syntax=python