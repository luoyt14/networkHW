"""
@author: Yantian Luo
@contact: lyt18@mails.tsinghua.edu.cn
@file: bgp_main.py.py
@time: 2019/6/23 12:13
"""
import os
from tqdm import tqdm
import matplotlib
import re
import json
matplotlib.use('tkAgg')
import matplotlib.pyplot as plt
import time


DATA_ROOT = '/tmp/data'
BGP_IPV4_PATH = os.path.join(DATA_ROOT, 'ipv4_bgp.txt')
BGP_IPV6_PATH = os.path.join(DATA_ROOT, 'ipv6_bgp.txt')
TIME_BIN = 60 * 60 * 24 * 7
BASE_TIME = "Apr 13 00:00:00 2019"


def filter_as_num(line):
    element_list = list(filter(lambda x: x.isdigit(), re.split(r'[,\s\n]', line)))
    if element_list:
        return element_list[-1]
    else:
        return False


def filter_time_info(line):
    element_list = line.split()[-4:]
    time_str = ' '.join(element_list)
    try:
        curr_time = time.strptime(time_str, '%b %d %H:%M:%S %Y')
        base_time = time.strptime(BASE_TIME, '%b %d %H:%M:%S %Y')
        curr_time_seconds = time.mktime(curr_time)
        base_time_seconds = time.mktime(base_time)
        bin_num = int(curr_time_seconds - base_time_seconds) // TIME_BIN
        return bin_num
    except ValueError:
        return False


def get_as_num(filename):
    info_line = 0
    ip_as_set = {}
    ip_as_time_set = {}
    with open(filename) as f:
        for line in tqdm(f):
            line = line.strip()
            if line == '':
                continue
            elif line[0] == '#':
                continue
            elif line[0] == '%':
                info_line = 0
                continue
            else:
                info_line += 1
                if info_line == 1:
                    original_address = line.split()[-1]
                elif info_line == 5:
                    as_num = filter_as_num(line.strip())
                elif info_line == 8:
                    info_line = 0
                    time_bin = filter_time_info(line)
                    if as_num and time_bin:
                        ip_as_set[original_address] = as_num
                        ip_as_time_set[original_address] = (as_num, time_bin)
    return ip_as_set, ip_as_time_set


def analyse_as_info(as_info_filename, as_list):
    with open(as_info_filename) as f:
        as_info_dict = json.loads(f.read())
    area_info_set = {}
    operator_info_set = {}
    for as_num in as_list:
        if as_num in as_info_dict:
            area_info = as_info_dict[as_num]['Country']
            operator_info = as_info_dict[as_num]['Name']
            if area_info not in area_info_set:
                area_info_set[area_info] = 1
            else:
                area_info_set[area_info] += 1
            if operator_info not in operator_info_set:
                operator_info_set[operator_info] = 1
            else:
                operator_info_set[operator_info] += 1
    return area_info_set, operator_info_set


def draw_pie_graph(info_set, save_num=0, save_type='ipv4'):
    info_list = sorted(info_set.items(), key=lambda x: x[1], reverse=True)
    sizes = [item[1] for item in info_list[:10]]
    labels = [item[0] for item in info_list[:10]]
    plt.figure()
    plt.pie(sizes,
            labels=labels,
            shadow=False,
            autopct='%2.000f%%',
            startangle=90)
    plt.axis('equal')
    plt.rcParams['figure.figsize'] = [20, 10]
    plt.legend(loc='upper left', bbox_to_anchor=(-0.1, 1))
    plt.savefig(f"{save_type}_{save_num}.png")
    plt.close()
    # plt.show()


def process_as_time_set(as_time_set):
    time_as_set = {}
    for key, value in tqdm(as_time_set.items()):
        if value[1] not in time_as_set:
            time_as_set[value[1]] = [value[0]]
        else:
            time_as_set[value[1]].append(value[0])
    return time_as_set


def draw_time_distribution(as_info_filename, time_as_set, save_type='ipv4'):
    max_area_num_list, max_operator_num_list = [], []
    time_num = 1
    for time_bin, as_list in tqdm(time_as_set.items()):
        area_info_set, operator_info_set = analyse_as_info(as_info_filename, as_list)
        max_area_num = max(list(area_info_set.values())) / sum(list(area_info_set.values()))
        max_area_num_list.append(max_area_num)
        max_operator_num = max(list(operator_info_set.values())) / sum(list(operator_info_set.values()))
        max_operator_num_list.append(max_operator_num)
        draw_pie_graph(area_info_set, save_num=time_num, save_type=save_type+'_area')
        draw_pie_graph(operator_info_set, save_num=time_num, save_type=save_type+'_operator')
        time_num += 1

    plt.figure()
    plt.plot(max_area_num_list, 'ro-')
    plt.xlabel('time bin(s)')
    plt.ylabel('the most area proportion')
    plt.title('Area distribution vs time')
    plt.savefig(f'area_distribution_{save_type}.png')
    plt.close()

    plt.figure()
    plt.plot(max_operator_num_list, 'bo-')
    plt.xlabel('time bin(s)')
    plt.ylabel('the most operator proportion')
    plt.title('Operator distribution vs time')
    plt.savefig(f'operator_distribution_{save_type}.png')
    plt.close()


if __name__ == '__main__':
    bgp_ipv4_path = 'ipv4_bgp.txt'
    bgp_ipv6_path = 'ipv6_bgp.txt'
    as_info_path = 'as_info.json'
    ipv4_as_set, ipv4_as_time_set = get_as_num(bgp_ipv4_path)
    ipv6_as_set, ipv6_as_time_set = get_as_num(bgp_ipv6_path)
    # ipv4_as_list = list(ipv4_as_set.values())
    # ipv6_as_list = list(ipv6_as_set.values())
    # print(list(ipv4_as_set.values())[:5])
    # print(list(ipv6_as_set.values())[:5])
    # ipv4_area_info_set, ipv4_operator_info_set = analyse_as_info(as_info_path, ipv4_as_list)
    # ipv6_area_info_set, ipv6_operator_info_set = analyse_as_info(as_info_path, ipv6_as_list)
    # draw_pie_graph(ipv4_area_info_set)
    # draw_pie_graph(ipv4_operator_info_set)
    # draw_pie_graph(ipv6_area_info_set)
    # draw_pie_graph(ipv6_operator_info_set)

    # 时序分析
    ipv4_time_bin_list = list(set([value[1] for value in ipv4_as_time_set.values()]))
    print(max(ipv4_time_bin_list))
    ipv6_time_bin_list = list(set([value[1] for value in ipv6_as_time_set.values()]))
    print(max(ipv6_time_bin_list))

    ipv4_time_as_set = process_as_time_set(ipv4_as_time_set)
    ipv6_time_as_set = process_as_time_set(ipv6_as_time_set)
    draw_time_distribution(as_info_path, ipv4_time_as_set, save_type='ipv4')
    draw_time_distribution(as_info_path, ipv6_time_as_set, save_type='ipv6')
