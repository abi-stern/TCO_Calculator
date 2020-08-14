import math 
m1s_medium = {
    "cores" : 24,
    "memory" : 384,
    "storage" : 23,
    "price_per_node_month" : 3469,
    "discount" : 0.3
    }

m1d_medium = {
    "cores" : 48,
    "memory" : 768,
    "storage" : 23,
    "price_per_node_month" : 5097,
    "discount" : 0.3
    }

R1 = {
    "facilities_per_month" : 1250,
    "nodes" : 5
    }

R2 = {
    "facilities_per_month" : 2700,
    "nodes" : 16
    }


def calculate_dimension_tco(inputs, number_of_vms):
    total_vCPUs = inputs["vCPU"] * number_of_vms
    total_memory = inputs["memory"] * number_of_vms

    nodes_cpu_bound = math.ceil(total_vCPUs/(inputs["node"]["cores"]*inputs["cpu_oversubscription"]))
    nodes_memory_bound = math.ceil(total_memory/(inputs["node"]["memory"]*inputs["memory_oversubscription"]))
    nodes = max(nodes_cpu_bound, nodes_memory_bound) if max(nodes_cpu_bound, nodes_memory_bound) > 3 else 3


    upfront_cost = (nodes * inputs["node"]["price_per_node_month"] * (1 - inputs["node"]["discount"]) * 36)/1000


    r1_number_of_racks = math.ceil(nodes/R1["nodes"]) 
    r1_cost = r1_number_of_racks * 36 * R1["facilities_per_month"] / 1000

    r2_number_of_racks = math.ceil(nodes/R2["nodes"]) 
    r2_cost = r2_number_of_racks * 36 * R2["facilities_per_month"] / 1000

    facilities_cost = min(r1_cost, r2_cost)

    number_of_racks = r1_number_of_racks if r1_cost < r2_cost else r2_number_of_racks

    total_cost = upfront_cost + facilities_cost

    return number_of_racks, total_cost

