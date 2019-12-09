import os
from tqdm import tqdm
import matplotlib
matplotlib.use('tkAgg')
import matplotlib.pyplot as plt
import pandas as pd
from utils import judge_address_type, judge_os_type


DATA_ROOT = '/tmp/data'
CLIENT_PATH = os.path.join(DATA_ROOT, 'client.log')
IVISERVER_PATH = os.path.join(DATA_ROOT, 'iviserver.log')


class UserInfo:
    def __init__(self, ipv4_address, ipv6_address, port, os_info):
        self.ipv4_address = ipv4_address
        self.ipv6_address = ipv6_address
        self.port = port
        self.os_info = os_info


def analyse_client_log(filename):
    ipv4_list = []
    ipv6_list = []
    os_set = {}
    os_list = []
    port_list = []
    with open(filename) as f:
        for line in tqdm(f):
            # sum up address info
            client_address = line.split()[4]
            if judge_address_type(client_address) == 4:
                ipv4_list.append(client_address)
            elif judge_address_type(client_address) == 6:
                ipv6_list.append(client_address)
            # sum up os info
            os_type = judge_os_type(line.split()[6:])
            port = int(line.split()[5])
            os_list.append(os_type)
            port_list.append(port)
            if os_type not in os_set:
                os_set[os_type] = 1
            else:
                os_set[os_type] += 1
    
    ipv4_num = len(set(ipv4_list))
    ipv6_num = len(set(ipv6_list))
    total_num = ipv4_num + ipv6_num
    print(f'ipv4 ratio = ipv4 / total = {ipv4_num} / {total_num} = {ipv4_num / total_num}')
    print(f'ipv6 ratio = ipv6 / total = {ipv6_num} / {total_num} ={ipv6_num / total_num}')
    print(f'total os types = {len(set(os_list))}')

    os_port = [os_list, port_list]
    
    return list(set(ipv4_list)), list(set(ipv6_list)), os_set, os_port


def analyse_iviserver_log(filename):
    ipv4_num, ipv6_num, ds_num, total = 0, 0, 0, 0
    ipv4_flag, ipv6_flag = False, False
    ipv4_temp_address, ipv6_temp_address = "", ""
    user_flag = 0
    address_set = {}
    with open(filename) as f:
        for line in tqdm(f):
            source_address = line.split()[-2]
            if judge_address_type(source_address) == 4:
                ipv4_flag = True
                ipv4_temp_address = source_address
            elif judge_address_type(source_address) == 6:
                ipv6_flag = True
                ipv6_temp_address = source_address
            if user_flag < 2:
                user_flag += 1
            else:
                total += 1
                user_flag = 0
                if ipv4_flag and ipv6_flag:
                    ds_num += 1
                    if ipv4_temp_address not in address_set and ipv4_temp_address != "":
                        address_set[ipv4_temp_address] = 0  # 0 代表双栈
                    if ipv6_temp_address not in address_set and ipv6_temp_address != "":
                        address_set[ipv6_temp_address] = 0
                elif ipv4_flag:
                    ipv4_num += 1
                    if ipv4_temp_address not in address_set and ipv4_temp_address != "":
                        address_set[ipv4_temp_address] = 1  # 1 代表v4
                elif ipv6_flag:
                    ipv6_num += 1
                    if ipv6_temp_address not in address_set and ipv6_temp_address != "":
                        address_set[ipv6_temp_address] = 2  # 2 代表v6
                ipv4_flag, ipv6_flag = False, False
                ipv4_temp_address, ipv6_temp_address = "", ""

    print(f'ipv4 ratio = ipv4 / total = {ipv4_num} / {total} = {ipv4_num / total}')
    print(f'ipv6 ratio = ipv6 / total = {ipv6_num} / {total} ={ipv6_num / total}')
    print(f'ds ratio = ds / total = {ds_num} / {total} ={ds_num / total}')

    sizes = [ipv4_num, ipv6_num, ds_num]
    labels = ['ipv4 users', 'ipv6 users', 'ds users']
    plt.pie(sizes,
            labels=labels,
            shadow=False,
            autopct='%2.000f%%',
            startangle=90)
    plt.axis('equal')
    plt.rcParams['figure.figsize'] = [20, 10]
    plt.legend(loc='upper left', bbox_to_anchor=(-0.1, 1))
    plt.show()

    return address_set


def analyse_os_type_ratio(os_set):
    os_list = sorted(os_set.items(), key=lambda x: x[1], reverse=True)
    sizes = [item[1] for item in os_list[:5]]
    labels = [item[0] for item in os_list[:5]]
    plt.pie(sizes, 
            labels=labels, 
            shadow=False, 
            autopct='%2.0f%%', 
            startangle=90)
    plt.axis('equal')
    plt.rcParams['figure.figsize']=[20,10]
    plt.legend(loc='upper left', bbox_to_anchor=(-0.1, 1))
    plt.show()


def analyse_os_port(os_port):
    os_list, port_list = os_port
    os_num = len(set(os_list))
    os_single_list = list(set(os_list))
    os_encode_dict = {item: k for k, item in enumerate(os_single_list)}
    os_encode_list = [os_encode_dict[item] for item in os_list]
    os_port_df = pd.DataFrame({'os_type_encode': os_encode_list, 'port': port_list})
    print(os_port_df.corr())
    plt.scatter(os_encode_list, port_list)
    plt.show()
    print(os_single_list)
    # print(pd.crosstab(os_port_df['os_type'], os_port_df['port']))


def os_user_distribution(address_set, client_path, os_name):
    ipv4_num, ipv6_num, ds_num, total = 0, 0, 0, 0
    with open(client_path) as f:
        for line in f:
            os_type = judge_os_type(line.split()[6:])
            source_address = line.split()[4]
            if os_type == os_name:
                if source_address not in address_set:
                    continue
                if address_set[source_address] == 0:
                    ds_num += 1
                elif address_set[source_address] == 1:
                    ipv4_num += 1
                elif address_set[source_address] == 2:
                    ipv6_num += 1
                total += 1

    print(f'ipv4 ratio = ipv4 / total = {ipv4_num} / {total} = {ipv4_num / total}')
    print(f'ipv6 ratio = ipv6 / total = {ipv6_num} / {total} ={ipv6_num / total}')
    print(f'ds ratio = ds / total = {ds_num} / {total} ={ds_num / total}')

    sizes = [ipv4_num, ipv6_num, ds_num]
    labels = ['ipv4 users', 'ipv6 users', 'ds users']
    plt.pie(sizes,
            labels=labels,
            shadow=False,
            autopct='%2.000f%%',
            startangle=90)
    plt.axis('equal')
    plt.rcParams['figure.figsize'] = [20, 10]
    plt.legend(loc='upper left', bbox_to_anchor=(-0.1, 1))
    plt.show()




if __name__ == '__main__':
    client_path = 'client.log'
    iviserver_path = 'iviserver.log'
    ipv4_list, ipv6_list, os_set, os_port = analyse_client_log(client_path)
    analyse_os_port(os_port)
    # analyse_os_type_ratio(os_set)
    # address_set = analyse_iviserver_log(iviserver_path)
    # os_user_distribution(address_set, client_path, 'win32')
    # os_user_distribution(address_set, client_path, 'iphone')
