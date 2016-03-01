# coding:utf-8
from base64 import b64encode
from time import sleep
from requests import get

router_url = 'http://192.168.1.1/'
username = 'admin'
password = 'prince'


def size_convert(size):
    units = ['KB', 'MB', 'GB', 'TB']
    for u in units:
        size /= 1024.0
        if size < 1024:
            return '%.2f%s/s' % (size, u)


def get_page(url):
    headers = {'Referer': router_url + 'userRpm/MenuRpm.htm'}
    cookies = {'Authorization': 'Basic%20' + b64encode(username + ':' + password)
        }
    params = {
        'contType': 1,
        'sortType': 1,
        'Refresh': '刷+新',
        'Num_per_page': 100,
        'Goto_page': 1
        }

    return get(url, params=params, cookies=cookies, headers=headers).content


def print_data():
    dhcp_url = router_url + 'userRpm/AssignedIpAddrListRpm.htm'
    traffic_url = router_url + 'userRpm/SystemStatisticRpm.htm'

    start = 'new Array(\n'
    end = '\n0,0 );'

    # get dhcp client
    content = get_page(dhcp_url)

    data = content[content.find(start) + len(start): content.find(end)].split('\n')
    clients = dict(
        zip(
            map(lambda x: x[1:-2], data[1::4]),
            map(lambda x: x[1:-2], data[::4])
        )
    )

    # get traffic data
    content = get_page(traffic_url)

    data = content[content.find(start) + len(start): content.find(end)].split('\n')
    data = map(lambda x: x.split(',')[1:7], data)
    data = map(
        lambda x: [x[0][1:-1] + ':' + clients.get(x[1][1:-1], '')] + map(int, x[4:]),
        data
        )

    data.sort(lambda x, y: -cmp(x[1], y[1]))

    data = map(lambda x: [x[0], size_convert(x[1]), size_convert(x[2])], data)
    data = filter(lambda x: not(x[1] == x[2] == '0.00KB/s'), data)

    for user, downstream, upstream in data:
        print ('%-40s down: %10s up: %10s') % (user, downstream, upstream)


if __name__ == '__main__':
    while True:
        print '-' * 30
        print_data()
        sleep(1)
