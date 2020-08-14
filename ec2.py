import math 
from dimension import calculate_dimension_tco

cisco_csr = {
    "t2.medium_infra" : 12, 
    "t2.medium_software" : 1942, 
    "c4.2xlarge_infra" : 113, 
    "c4.2xlarge_software" : 5804,
    "c4.4xlarge_infra" : 226, 
    "c4.4xlarge_software" : 7572,
    }

def calculate_security_cost(number_of_vms, number_of_racks):
    if number_of_vms <=10:
        infra = 36 * cisco_csr["t2.medium_infra"] * number_of_racks / 1000 
        software = 3 * cisco_csr["t2.medium_software"] * number_of_racks / 1000 
        return infra + software
    elif number_of_vms <= 50:
        infra = 36 * cisco_csr["c4.2xlarge_infra"] * number_of_racks / 1000 
        software = 3 * cisco_csr["c4.2xlarge_software"] * number_of_racks / 1000 
        return infra + software
    else:
        infra = 36 * cisco_csr["c4.4xlarge_infra"] * number_of_racks / 1000 
        software = 3 * cisco_csr["c4.4xlarge_software"] * number_of_racks / 1000 
        return infra + software

def calculate_blind_spot_cost(instance, number_of_vms):
    return ( (instance["rehosting"] + instance["reskilling"])/100 ) * number_of_vms / 1000


def calculate_ec2_tco_without_blind_spot(instance, dimension, number_of_vms, storage):

    upfront_cost = instance["price_per_month"] * (1 - instance["discount"]) * number_of_vms * 36 / 1000

    egress_cost = instance["egress"] * upfront_cost

    ebs_cost = number_of_vms * storage * instance["ebs_gb_month"] * 36 / 1000

    number_of_racks, dimension_tco = calculate_dimension_tco(dimension, number_of_vms)

    security_cost = calculate_security_cost(number_of_vms, number_of_racks)

    return upfront_cost + egress_cost + ebs_cost + security_cost


def calculate_ec2_tco_with_blind_spot(instance, dimension, number_of_vms, storage):

    return calculate_ec2_tco_without_blind_spot(instance, dimension, number_of_vms, storage) + calculate_blind_spot_cost(instance, number_of_vms)


