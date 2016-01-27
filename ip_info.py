OWNERS = {
    'Google': 1,
    'Facebook': 2,
    'Twitter': 3,
    'Amazon': 4,
    'Yahoo': 5,
    'Microsoft': 6,
    'Hetzner Online Ag': 7,
}

ip_range = {}

def get_info(ip):
    ip_long = ip_to_long(ip)
    for owner in ip_range:
    	if is_belong_to(ip_long, ip_range[owner]):
    		return {
    			'owner': owner,
    			'owner_id': OWNERS[owner]
    		}

    return {
        'owner': 'Unknown',
        'owner_id': -1
    }

def is_belong_to(ip, ip_owner):
	for rang in ip_owner:
		if is_inside(ip, rang):
			return True

def is_inside(ip, range):
	return ip >= range[0] and ip <= range[1]


def _init_():
	from ip_db import IPDB 

	for owner in IPDB:
		ip_string = IPDB[owner]
		ranges = []
		ip_range[owner] = ranges

		arr = ip_string.split(',')
		for s in arr:
			ips = s.split('-')
			ip0 = ip_to_long(ips[0].strip())
			ip1 = ip_to_long(ips[1].strip())
			ranges.append((ip0, ip1))

		print(owner, len(ranges))


def ip_to_long(ip):
	arr = ip.split('.')
	number = 0
	for i in range(0, len(arr)):
		n = int(arr[i])
		number += n << ((len(arr ) - i - 1 ) * 8)
	return number 


_init_()

# print(get_info("193.120.166.64"))
