
FAKE_DRIVER = None


class fake_driver(object):

    def __init__(self):
        return

    @classmethod
    def get_instance(cls):
        global FAKE_DRIVER
        if not FAKE_DRIVER:
            FAKE_DRIVER = cls()
        return FAKE_DRIVER

        # this is a vlan operation
    def creat_vlan(self, context, vlan_infos):
        return {"creat_vlan": "success"}

    def del_vlan(self, context, id_, vlan_infos):
        return {"del_vlan": "success"}

    def get_vlan(self, context, vlan_infos):
        return {"get_vlan": "success"}

    def get_vlans(self, context, vlan_infos):
        return {"get_vlans": "success"}

    # this is a netservice operation
    def creat_netservice(self, context, netsev_infos):
        return {"creat_netservice": "success"}

    def del_netservice(self, context, id_, netsev_infos):
        return {"del_netservice": "success"}

    def get_netservice(self, context, netsev_infos):
        return {"get_netservice": "success"}

    def get_netservices(self, context, netsev_infos):
        return {"get_netservices": "success"}

    # this is a addrobj operation
    def add_addrobj(self, context, addrobj_infos):
        return {"add_addrobj": "success"}

    def del_addrobj(self, context, addrobj_infos):
        return {"del_addrobj": "success"}

    def get_addrobj(self, context, addrobj_infos):
        return {"get_addrobj": "success"}

    def get_addrobjs(self, context, addrobj_infos):
        return {"get_addrobjs": "success"}
