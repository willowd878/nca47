from oslo_config import cfg

from nca47.common.i18n import _

API_SERVICE_OPTS = [
    cfg.StrOpt('host_ip',
               default='0.0.0.0',
               help=_('The IP address on which nca47-api listens.')),
    cfg.PortOpt('port',
                default=8080,
                help=_('The TCP port on which nca47-api listens.')),
    cfg.IntOpt('max_limit',
               default=1000,
               help=_('The maximum number of items returned in a single '
                      'response from a collection resource.')),
    cfg.StrOpt('public_endpoint',
               default=None,
               help=_("Public URL to use when building the links to the API "
                      "resources (for example, \"https://nca47.rocks:6384\")."
                      " If None the links will be built using the request's "
                      "host URL. If the API is operating behind a proxy, you "
                      "will want to change this to represent the proxy's URL. "
                      "Defaults to None.")),
    cfg.IntOpt('api_workers',
               help=_('Number of workers for OpenStack nca47 API service. '
                      'The default is equal to the number of CPUs available '
                      'if that can be determined, else a default worker '
                      'count of 1 is returned.')),
    cfg.BoolOpt('enable_ssl_api',
                default=False,
                help=_("Enable the integrated stand-alone API to service "
                       "requests via HTTPS instead of HTTP. If there is a "
                       "front-end service performing HTTPS offloading from "
                       "the service, this option should be False; note, you "
                       "will want to change public API endpoint to represent "
                       "SSL termination URL with 'public_endpoint' option.")),
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='api',
                         title='Options for the nca47-api service')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)
