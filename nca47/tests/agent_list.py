import sys
from oslo_config import cfg
import cStringIO
import operator
from oslo_utils import timeutils
from nca47 import objects
from nca47.common.i18n import _
from nca47.common import service as nca47_service

sys.path.append('/vagrant/nca47/')
CONF = cfg.CONF
context = {}

AGENT_OPTS = [
    cfg.IntOpt('agent_down_time',
               default='120',
               help=_('Seconds to regard the agent is down; should be at '
                      'least twice report_interval, to be sure the '
                      'agent is down for good.')),
]

opt_group = cfg.OptGroup(name='agent',
                         title='Options for nca47 agent node info')
CONF.register_group(opt_group)
CONF.register_opts(AGENT_OPTS, opt_group)


def indent(rows, hasHeader=False, headerChar='-', delim=' | ', justify='left',
           separateRows=False, prefix='', postfix='', wrapfunc=lambda x: x):

    def rowWrapper(row):
        newRows = [wrapfunc(item).split('\n') for item in row]
        return [[substr or '' for substr in item] for item in map(None,
                                                                  *newRows)]
    # break each logical row into one or more physical ones
    logicalRows = [rowWrapper(row) for row in rows]
    # columns of physical rows
    columns = map(None, *reduce(operator.add, logicalRows))
    # get the maximum of each column by the string length of its items
    maxWidths = [max([len(str(item)) for item in column]) for column in
                 columns]
    rowSeparator = headerChar * (len(prefix) + len(postfix) +
                                 sum(maxWidths) +
                                 len(delim)*(len(maxWidths)-1))
    # select the appropriate justify method
    mode_dict = {'center': str.center, 'right': str.rjust, 'left': str.ljust}
    justify = mode_dict[justify.lower()]
    output = cStringIO.StringIO()
    if separateRows:
        print >> output, rowSeparator
    for physicalRows in logicalRows:
        for row in physicalRows:
            print >> output, \
                prefix \
                + delim.join([justify(str(item), width) for (item, width) in
                              zip(row, maxWidths)]) + postfix
        if separateRows or hasHeader:
            print >> output, rowSeparator
            hasHeader = False
    return output.getvalue()


def wrap_onspace(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line, ' \n'[(len(line[line.rfind('\n')+1:]) +
                                len(word.split('\n', 1)[0]) >= width)], word),
                  text.split(' '))


if __name__ == '__main__':
    nca47_service.prepare_service(sys.argv)
    labels = ('id', 'agent_type', 'agent_ip', 'agent_nat_ip', 'status')
    agents = objects.Agent(context)
    agent_list = agents.get_objects(context)
    print agent_list
    rows = []
    for agent in agent_list:
        row = []
        row.append(agent.id)
        row.append(agent.agent_type)
        row.append(agent.agent_ip)
        row.append(agent.agent_nat_ip)
        is_down = timeutils.is_older_than(agent.update_time,
                                          CONF.agent.agent_down_time)
        agent_status = "xxx" if is_down else ':-)'
        row.append(agent_status)
        rows.append(row)
    width = 10

    print indent([labels]+rows, hasHeader=True, separateRows=True,
                 prefix='| ', postfix=' |',
                 wrapfunc=lambda x: wrap_onspace(x, width))
