from nca47.common.exception import Invalid
from nca47.common.i18n import _

EZDNS = {
    1: 'any or none acl is read only',
    2: 'acl already exists',
    3: 'operate non-exist acl',
    4: 'dns64 prefix should be a ipv6 addr',
    5: 'invalid dns64 prefix netmask',
    6: 'suffix is needed if netmask of prefix smaller than 96',
    7: 'DNS64 setting already exists',
    8: 'operate non-exist DNS64 setting',
    9: 'tsig key already exists',
    10: 'delete acl is using by view',
    11: 'operate non-exist zone',
    12: 'cache file not exist',
    13: 'cache size too large',
    14: 'operate non-exist view',
    15: 'get zone from backend server failed',
    16: 'zone already exists',
    17: 'unsupported meta data type',
    18: 'view already exists',
    19: 'delete default view',
    20: "cann't modify acl of default view",
    21: 'operate non-exist rr',
    22: 'conflict key secret',
    23: 'not supported zone type',
    24: 'operate non-exist shared rr',
    25: "cann't delete the last shared rr",
    26: 'operate non-exist tsig key',
    27: 'reconfig dns server failed',
    28: 'no rndc-confgen installed',
    29: 'lack/white list already exists',
    30: 'operate non-exist back/white list',
    31: "zone owner doesn't has view owner",
    32: 'unsupport acl action',
    33: 'no pine-control installed',
    34: 'server already started',
    35: 'RR format error',
    36: 'zone transfer failed',
    37: 'more than one ad zone owner',
    38: 'update zone failed',
    39: 'shared rr already exists',
    40: 'add duplicate rr',
    41: 'add exclusive rr',
    42: 'short of glue rr',
    43: 'conflict with exists cname',
    44: 'delete unknown rr',
    45: "can't delete soa rr",
    46: 'no ns left after delete',
    47: 'delete glue needed by other rr',
    48: "reverse zone doesn't exist",
    49: 'rdata is valid',
    50: 'rr is out of zone',
    51: "onfigure value isn't valid",
    52: 'unknown forward style',
    53: 'duplicate zone master',
    54: 'forwarder exists',
    55: 'operate non-exist forwarder',
    56: 'operate non-exist view on node',
    57: 'already exists root zone',
    58: 'only A/AAAA NS is allowed in hint zone',
    59: 'already has root configuration',
    60: "rr type isn't supported",
    61: "can't update slave zone",
    62: 'duplicate local domain policy',
    63: "zone name isn't valid",
    64: 'add duplicate host',
    65: 'soa serial number degraded',
    66: "root isn't support in local policy",
    67: 'auth zone with same name already exists',
    68: 'stub zone with same name already exists',
    69: 'forward zone with same name already exists',
    70: 'acl is used by view',
    71: 'acl is used by AD zone',
    72: 'rrl policy already exist',
    73: 'non-exist rrl policy',
    74: 'delete monitor strategy in use',
    75: 'monitor strategy already exist',
    76: 'non exist monitor strategy',
    77: "node's view querysource already exists",
    78: "node's view querysource not exist",
    79: 'too much rrls(over 999)',
    100: 'version is unknown',
    101: 'patch file broken',
    102: "source code isn't a release version",
    103: 'binding different iface with same ip address',
    104: 'ntp interval out of range',
    105: 'send a test mail failed, check the configuration',
    300: 'invalid ip address',
    301: 'no dns server installed',
    302: 'not enough params',
    303: 'not supported backup method',
    304: 'not supported command method',
    305: "service hasn't been init",
    306: 'not supported ha type',
    307: 'member is not accessible',
    308: 'wrong username and password',
    309: 'nic config failed',
    310: "service hasn't been started",
    311: 'init params is required',
    312: 'invalid port',
    313: 'verify node failed',
    314: 'request body json format error',
    315: 'connect backup server timeout',
    316: 'data recovery failed',
    317: 'data backup failed',
    318: 'lower limit bigger than upper limit',
    319: 'execute command timeout',
    320: 'password/role failed',
    404: 'Wrong url, please check it',
    600: 'operate non-exist group',
    601: 'member with same ip alreasy exists',
    602: 'member with same name alreasy exists',
    603: 'operate non-exist member',
    604: 'not supported service type',
    605: 'member command queue is full',
    606: 'member is performing data recovery',
    607: 'group already exists',
    608: "cann't operate local group",
    609: 'user already exists',
    610: 'operate non-exist user',
    611: 'init member service failed',
    612: 'owners is required',
    613: "cann't delete the last owner for resource",
    614: 'add duplicate owners',
    615: 'old password is wrong',
    616: "cann't delete local group",
    617: "cann't delete local member",
    618: 'permission denied',
    619: 'unkown authority rule',
    620: 'authority rule already exist',
    621: 'invalid backup data',
    622: 'device already under management',
    623: "some devices don't exist any more",
    624: "cann't operation inactive cloud'",
    625: "cann't add multi backup devices'",
    626: 'no backup device',
    627: 'not master device',
    628: 'not backup device',
    629: 'not slave device',
    630: "hasn't managed by cloud yet",
    631: "node can't communicate with master",
    632: 'invalid exception handle method',
    800: 'time out while sending alarm msg',
}


class ZdnsErrMessage(Invalid):
    _msg_fmt = None

    def __init__(self, cord):
        self._msg_fmt = _(cord + ":" + EZDNS[cord])
