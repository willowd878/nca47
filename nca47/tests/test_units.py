import re
from nca47.common.exception import BadRequest


def _valid_port(port):
    reg = r'^([0-9]{1,5}[-][0-9]{1,5})$'
    match_obj = re.search(reg, port)
    if match_obj is None:
        raise BadRequest()
    print match_obj.group(0)
    port_list = match_obj.group(0).split('-')
    port1 = int(port_list[0])
    print port1
    port2 = int(port_list[1])
    if port1 > 65535 | port2 > 65535:
        raise BadRequest()
    else:
        if port1 > port2:
            raise BadRequest()
    return None


if __name__ == '__main__':
    test_array = ['a', 'b', 'c']
    if ('d' and 'b' in test_array:
        print 'dddd'
    print test_array
