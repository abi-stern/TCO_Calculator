def build_azure_cost_curves(instance, scenario):
    all_azure_cost_curves = []
    all_dimension_cost_curves = []

    flags = [False, True]
      
    for blind_cost_flag in flags:
        for dimension_node_type, dimension_node in dimension_nodes.items(): 
            blind_cost = "with" if blind_cost_flag else "without"
            dimension = dimension_node.copy()
            dimension["vCPU"] = instance["vCPU"]
            dimension["memory"] = instance["memory"]

            dimension_cost_curve = []
            dimension_cost_curve.append(dimension_node_type + "_" + str(instance["vCPU"]) + "_" + str(instance["memory"]))
            for number_of_vms in range(vm_start, vm_end, vm_increment):
                racks, dimension_tco = calculate_dimension_tco(dimension, number_of_vms)
                dimension_cost_curve.append(str(round(dimension_tco/number_of_vms, 2)))

            all_dimension_cost_curves.append(dimension_cost_curve)

            for storage in range(storage_start, storage_end, storage_increment):
                azure_cost_curve = []
                azure_cost_curve.append(dimension["alias"] + "_" + instance["name"] + "_" + str(storage) + "_" + blind_cost)
                for number_of_vms in range(vm_start, vm_end, vm_increment):

                    azure_tco_per_vm = calculate_azure_tco_with_blind_spot(instance, dimension, number_of_vms, storage, scenario) / number_of_vms if blind_cost_flag else calculate_azure_tco_without_blind_spot(instance, dimension, number_of_vms, storage, scenario) / number_of_vms
                    azure_cost_curve.append(round(azure_tco_per_vm,2))

                all_azure_cost_curves.append(azure_cost_curve)

    return all_dimension_cost_curves, all_azure_cost_curves