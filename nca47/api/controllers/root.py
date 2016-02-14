import pecan

from nca47.api.controllers.v1 import root as v1


class RootController(object):
    def __init__(self):
        self.v1 = v1.V1Controller()
        return

    @pecan.expose('json')
    def index(self):
        base_url = pecan.request.application_url
        available = [{'tag': 'v1', 'date': '2016-02-01T00:00:00Z', }]
        collected = [version_descriptor(base_url, v['tag'], v['date'])
                     for v in available]
        versions = {'versions': {'values': collected}}
        return versions


def version_descriptor(base_url, version, released_on):
    url = version_url(base_url, version)
    return {
        'id': version,
        'links': [
            {'href': url, 'rel': 'self', },
        ],
        'status': 'stable',
        'updated': released_on,
    }


def version_url(base_url, version_number):
    return '%s/%s' % (base_url, version_number)
