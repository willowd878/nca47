import sys
import requests
import MySQLdb
import uuid
import json

# the host of mysql ip
mysql_host = sys.argv[1]
# the user of mysql
mysql_user = sys.argv[2]
# the passwd of mysql
mysql_passwd = sys.argv[3]
# the host of device
device_host = sys.argv[4]
# the port of device
device_port = sys.argv[5]


def main():
    """synchronization the database from the device"""
    conn, cur = db_connect_open()
    cur.execute('delete from dns_rrs_info')
    cur.execute('delete from dns_zone_info')
    get_zones_device(conn, cur)
    conn.commit()
    db_connect_close
    print "Data synchronization from device success !"


def db_connect_open():
    """get the connection from mysql db"""
    try:
        conn = MySQLdb.connect(host=mysql_host, user=mysql_user,
                               passwd=mysql_passwd, port=3306, charset='utf8')
        conn.select_db('nca47')
        cur = conn.cursor()
        return conn, cur
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        exit(1)


def db_connect_close(conn, cur):
    """close the connection from mysql db"""
    cur.close()
    conn.close()


def get_zones_device(conn, cur):
    """get the all zones from device"""
    url = "https://" + device_host + ":" + device_port + "/views/default/zones"
    auth = ("admin", "zdns")
    response = requests.get(url, data={"current_user": "admin"},
                            auth=auth, verify=False)
    if ('error' in response.json().keys()) or (response is None):
        print "The data of dns_zone_info from device is null !"
        exit(1)
    for resourc in response.json()['resources']:
        if resourc['name'] != '@':
            zone_uuid = uuid.uuid4()
            owners = json.dumps(resourc['owners'], encoding='UTF-8',
                                ensure_ascii=False)
            masters = json.dumps(resourc['masters'], encoding='UTF-8',
                                 ensure_ascii=False)
            slaves = json.dumps(resourc['slaves'], encoding='UTF-8',
                                ensure_ascii=False)
            value = (zone_uuid, 'egfbank', resourc['name'], masters, slaves,
                     resourc['default_ttl'], resourc['renewal'], owners,
                     'MANUAL')
            cur.execute('insert into dns_zone_info (id, tenant_id, zone_name,'
                        'masters, slaves, default_ttl, renewal, owners,'
                        'operation_fro, deleted) values(%s, %s, %s, %s, %s,'
                        '%s, %s, %s, %s, False)', value)
            get_rrs_device(zone_uuid, cur, resourc['name'])


def get_rrs_device(zone_uuid, cur, zone_name):
    """get the record from device by the zone_name"""
    url = "https://" + device_host + ":" + device_port +\
        "/views/default/zones/" + zone_name + "/rrs"
    auth = ("admin", "zdns")
    response = requests.get(url, data={"current_user": "admin"},
                            auth=auth, verify=False)
    if ('error' in response.json().keys()) or (response is None):
        print "The data of dns_rrs_info from device is null !"
        exit(1)
    for resourc in response.json()['resources']:
        rrs_uuid = uuid.uuid1()
        value = [rrs_uuid, resourc['id'], zone_uuid, resourc['name'],
                 resourc['type'], resourc['ttl'], resourc['klass'],
                 resourc['rdata'], 'egfbank', 'MANUAL']
        cur.execute('insert into dns_rrs_info (id, rrs_id, zone_id, rrs_name,'
                    'type, ttl, klass, rdata, tenant_id, operation_fro,'
                    'deleted) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'
                    'False)', value)


if __name__ == '__main__':
    sys.exit(main())
