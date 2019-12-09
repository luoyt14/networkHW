import sys


def ipv4grouptoipv6(ipv4groupstr):
    res = hex(int(ipv4groupstr))[2:]
    if len(res)==2:
        return res
    else:
        return '0'+res


def processIPv4(ipv4str):
    numlist = ipv4str.split('.')
    return [ipv4grouptoipv6(item) for item in numlist]


def processIPv6(prefix):
    numlist = prefix.split(':')
    return numlist[:3]


def constructIPv6(prefix, ipv4str, suffix=0):
    prefixlist = processIPv6(prefix)
    ipv4numlist = processIPv4(ipv4str)
    reslist = [prefixlist[0], prefixlist[1]]
    group3 = prefixlist[2][:-2]+ipv4numlist[0]
    group3 = hex(int(group3, 16))[2:]
    reslist.append(group3)
    group4 = ipv4numlist[1]+ipv4numlist[2]
    group4 = hex(int(group4, 16))[2:]
    reslist.append(group4)
    group5 = ipv4numlist[3]
    group5 = hex(int(group5, 16))[2:]
    reslist.append(group5)
    res = ":".join(reslist) + "::"
    return res

if __name__ == '__main__':
    ipv4str = sys.argv[1]
    prefix = sys.argv[2]
    # ipv4str = '192.0.2.33'
    # prefix = '2001:db8:100::/40'
    print(constructIPv6(prefix, ipv4str))
