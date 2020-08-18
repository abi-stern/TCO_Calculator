# pow(2, math.ceil(math.log2(127)))

import math 
from dimension import calculate_dimension_tco
from azure_instances import managed_disk

cisco_csr = {
    "F2s_infra" : 28.33, 
    "F2s_software" : 1942, 
    "F8s_infra" : 114.78, 
    "F8s_software" : 5804,
    "F16s_infra" : 229.59, 
    "F16s_software" : 7572,
    }

def calculate_security_cost(number_of_vms, number_of_racks):
    if number_of_vms <=10:
        infra = 36 * cisco_csr["F2s_infra"] * number_of_racks / 1000 
        software = 3 * cisco_csr["F2s_software"] * number_of_racks / 1000 
        return infra + software
    elif number_of_vms <= 50:
        infra = 36 * cisco_csr["F8s_infra"] * number_of_racks / 1000 
        software = 3 * cisco_csr["F8s_software"] * number_of_racks / 1000 
        return infra + software
    else:
        infra = 36 * cisco_csr["F16s_infra"] * number_of_racks / 1000 
        software = 3 * cisco_csr["F16s_software"] * number_of_racks / 1000 
        return infra + software

def calculate_blind_spot_cost(instance, number_of_vms):
    return ( (instance["rehosting"] + instance["reskilling"])/100 ) * number_of_vms / 1000


def calculate_azure_tco_without_blind_spot(instance, dimension, number_of_vms, storage, scenario):

    if scenario == "linux":
        upfront_cost = instance["linux"] * (1 - instance["discount"]) * number_of_vms * 36 / 1000
    elif scenario == "windows_with_hybrid_benefit":
        upfront_cost = instance["windows_with_hybrid_benefit"] * (1 - instance["discount"]) * number_of_vms * 36 / 1000
    else:
        upfront_cost = instance["windows"] * (1 - instance["discount"]) * number_of_vms * 36 / 1000

    egress_cost = instance["egress"] * upfront_cost

    managed_disk_cost = 0 
    if storage > 0 :
        managed_disk_cost = number_of_vms * managed_disk[pow(2, math.ceil(math.log2(storage)))] * 36 / 1000

    number_of_racks, dimension_tco = calculate_dimension_tco(dimension, number_of_vms)

    security_cost = calculate_security_cost(number_of_vms, number_of_racks)

    return upfront_cost + egress_cost + managed_disk_cost + security_cost


def calculate_azure_tco_with_blind_spot(instance, dimension, number_of_vms, storage, scenario):

    return calculate_azure_tco_without_blind_spot(instance, dimension, number_of_vms, storage, scenario) + calculate_blind_spot_cost(instance, number_of_vms)


