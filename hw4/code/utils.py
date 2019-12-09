def judge_address_type(address):
    if '.' in address:
        return 4
    else:
        return 6


def judge_os_type(os_type_list):
    os_type_list = [item.lower() for item in os_type_list]
    return ' '.join(os_type_list)
