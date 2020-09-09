from dimension_nodes import dimension_nodes
from linux_ec2_instances import *
from windows_ec2_instances import *
from azure_instances import *
from dimension import calculate_dimension_tco
from ec2 import calculate_ec2_tco_with_blind_spot, calculate_ec2_tco_without_blind_spot
from azure import calculate_azure_tco_without_blind_spot, calculate_azure_tco_with_blind_spot

import xlsxwriter
import numpy
import math


#storage_start = 00
#storage_end = 1100
#storage_increment = 100

#vm_start = 50
#vm_end = 2050
#vm_increment = 50

storage_range = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000]
vm_range = [25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575, 600, 625, 650, 675, 700, 725, 750, 775, 800, 900, 1000, 1500, 2000]

def build_ec2_cost_curves(instance):
    all_ec2_cost_curves = []
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
            for number_of_vms in vm_range: #range(vm_start, vm_end, vm_increment):
                racks, dimension_tco = calculate_dimension_tco(dimension, number_of_vms)
                dimension_cost_curve.append(str(round(dimension_tco/number_of_vms, 2)))

            all_dimension_cost_curves.append(dimension_cost_curve)

            for storage in storage_range: #(storage_start, storage_end, storage_increment):
                ec2_cost_curve = []
                ec2_cost_curve.append(dimension["alias"] + "_" + instance["name"] + "_" + str(storage) + "_" + blind_cost)
                for number_of_vms in vm_range: #range(vm_start, vm_end, vm_increment):

                    ec2_tco_per_vm = calculate_ec2_tco_with_blind_spot(instance, dimension, number_of_vms, storage) / number_of_vms if blind_cost_flag else calculate_ec2_tco_without_blind_spot(instance, dimension, number_of_vms, storage) / number_of_vms
                    ec2_cost_curve.append(round(ec2_tco_per_vm,2))

                all_ec2_cost_curves.append(ec2_cost_curve)

    return all_dimension_cost_curves, all_ec2_cost_curves

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
            for number_of_vms in vm_range: #range(vm_start, vm_end, vm_increment):
                racks, dimension_tco = calculate_dimension_tco(dimension, number_of_vms)
                dimension_cost_curve.append(str(round(dimension_tco/number_of_vms, 2)))

            all_dimension_cost_curves.append(dimension_cost_curve)

            for storage in storage_range: #(storage_start, storage_end, storage_increment):
                azure_cost_curve = []
                azure_cost_curve.append(dimension["alias"] + "_" + instance["name"] + "_" + str(storage) + "_" + blind_cost)
                for number_of_vms in vm_range: #range(vm_start, vm_end, vm_increment):

                    azure_tco_per_vm = calculate_azure_tco_with_blind_spot(instance, dimension, number_of_vms, storage, scenario) / number_of_vms if blind_cost_flag else calculate_azure_tco_without_blind_spot(instance, dimension, number_of_vms, storage, scenario) / number_of_vms
                    azure_cost_curve.append(round(azure_tco_per_vm,2))

                all_azure_cost_curves.append(azure_cost_curve)

    return all_dimension_cost_curves, all_azure_cost_curves

def build_competitive_matrix(instance):

    intersection_points = {}
    transformed_competitive_matrix = []
    titles = ["M1s Medium without oversubscription", "M1s Medium with oversubscription", "M1d Medium without oversubscription", "M1d Medium with oversubscription"]
    blank = ["  ", "  ", "  ", "  ", "  "]
    competitive_matrix = []
    flags = [False, True]
      
    for blind_cost_flag in flags:
        competitive_matrix = []
        for dimension_node_type, dimension_node in dimension_nodes.items():
            dimension = dimension_node.copy()
            dimension["vCPU"] = instance["vCPU"]
            dimension["memory"] = instance["memory"]

            for storage in storage_range: #(storage_start, storage_end, storage_increment):
                for number_of_vms in vm_range: #range(vm_start, vm_end, vm_increment):

                    number_of_racks, dimension_tco = calculate_dimension_tco(dimension, number_of_vms)
                    dimension_tco_per_vm = dimension_tco / number_of_vms
                    ec2_tco_per_vm = calculate_ec2_tco_with_blind_spot(instance, dimension, number_of_vms, storage) / number_of_vms if blind_cost_flag else calculate_ec2_tco_without_blind_spot(instance, dimension, number_of_vms, storage) / number_of_vms

                    if dimension_tco_per_vm <= ec2_tco_per_vm:
                        percentage_better = round((ec2_tco_per_vm - dimension_tco_per_vm) * 100 / dimension_tco_per_vm, 1)
                        intersection_points[storage] = str(number_of_vms) #+ " (" + str(percentage_better) + "%)"
                        break

                    intersection_points[storage] = "EC2 better"

            competitive_matrix.append([value for key, value in intersection_points.items()])

        i = 0
        for storage in storage_range: #(storage_start, storage_end, storage_increment):
            temp = []
            for j in range(0, len(competitive_matrix), 1):
                temp.append(competitive_matrix[j][i])
            i = i + 1
            transformed_competitive_matrix.append([str(storage) + " Gb"] + temp)

    instance_name_with = [instance["name"] +  " with blind cost"] + titles
    instance_name_without = [instance["name"] +  " without blind cost"] + titles
        
    length = len(storage_range)  #len(list(range(storage_start, storage_end, storage_increment)))

    transformed_competitive_matrix.insert(0, instance_name_without)
    transformed_competitive_matrix.insert(length + 1 , instance_name_with)
    transformed_competitive_matrix.append(blank)

    return transformed_competitive_matrix

def build_competitive_matrix_azure(instance, scenario):

    intersection_points = {}
    transformed_competitive_matrix = []
    titles = ["M1s Medium without oversubscription", "M1s Medium with oversubscription", "M1d Medium without oversubscription", "M1d Medium with oversubscription"]
    blank = ["  ", "  ", "  ", "  ", "  "]
    competitive_matrix = []
    flags = [False, True]
      
    for blind_cost_flag in flags:
        competitive_matrix = []
        for dimension_node_type, dimension_node in dimension_nodes.items():
            dimension = dimension_node.copy()
            dimension["vCPU"] = instance["vCPU"]
            dimension["memory"] = instance["memory"]

            for storage in storage_range: #(storage_start, storage_end, storage_increment):
                for number_of_vms in vm_range: #range(vm_start, vm_end, vm_increment):

                    number_of_racks, dimension_tco = calculate_dimension_tco(dimension, number_of_vms)
                    dimension_tco_per_vm = dimension_tco / number_of_vms
                    azure_tco_per_vm = calculate_azure_tco_with_blind_spot(instance, dimension, number_of_vms, storage, scenario) / number_of_vms if blind_cost_flag else calculate_azure_tco_without_blind_spot(instance, dimension, number_of_vms, storage, scenario) / number_of_vms

                    if dimension_tco_per_vm <= azure_tco_per_vm:
                        percentage_better = round((azure_tco_per_vm - dimension_tco_per_vm) * 100 / dimension_tco_per_vm, 1)
                        intersection_points[storage] = str(number_of_vms) #+ " (" + str(percentage_better) + "%)"
                        break

                    intersection_points[storage] = "Azure better"

            competitive_matrix.append([value for key, value in intersection_points.items()])

        i = 0
        for storage in storage_range: #(storage_start, storage_end, storage_increment):
            temp = []
            for j in range(0, len(competitive_matrix), 1):
                temp.append(competitive_matrix[j][i])
            i = i + 1
            transformed_competitive_matrix.append([str(storage) + " Gb"] + temp)

    instance_name_with = [instance["name"] +  " with blind cost"] + titles
    instance_name_without = [instance["name"] +  " without blind cost"] + titles
        
    length = len(storage_range) #len(list(range(storage_start, storage_end, storage_increment)))

    transformed_competitive_matrix.insert(0, instance_name_without)
    transformed_competitive_matrix.insert(length + 1 , instance_name_with)
    transformed_competitive_matrix.append(blank)

    return transformed_competitive_matrix


def write_to_excel(file_name, data):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    x = 0
    y = 0 

    for row in data:
        y = 0
        for column in range(0, len(row), 1):
            worksheet.write(x, y, row[column])
            y = y + 1

        x = x + 1

    workbook.close()

ec2_cost_curve_data = []
azure_cost_curve_data = []
dimension_cost_curve_data = []
competitive_matrix_data = []


for instance_family_name, instance_family in all_ec2_instances_windows.items():
    competitive_matrix_data = []
    dimension_cost_curve_data = []
    ec2_cost_curve_data = []
    for instance_name, instance in instance_family.items():
        
        a, b = build_ec2_cost_curves(instance)
        dimension_cost_curve_data.extend(a)
        ec2_cost_curve_data.extend(b)
    
        competitive_matrix_data.extend(build_competitive_matrix(instance))

        write_to_excel("windows_" + instance_family_name[-2:] + "vcpu_dimension_cost_curves.xlsx", numpy.unique(dimension_cost_curve_data, axis = 0))
        write_to_excel("windows_" + instance_family_name[-2:] + "vcpu_ec2_cost_curves.xlsx", ec2_cost_curve_data)
        write_to_excel("windows_" + instance_family_name[-2:] + "vcpu_competitive_matrix.xlsx", competitive_matrix_data)


for instance_family_name, instance_family in all_ec2_instances_linux.items():
    competitive_matrix_data = []
    dimension_cost_curve_data = []
    ec2_cost_curve_data = []
    for instance_name, instance in instance_family.items():

        a, b = build_ec2_cost_curves(instance)
        dimension_cost_curve_data.extend(a)
        ec2_cost_curve_data.extend(b)
    
        competitive_matrix_data.extend(build_competitive_matrix(instance))

        write_to_excel("linux_" + instance_family_name[-2:] + "vcpu_dimension_cost_curves.xlsx", numpy.unique(dimension_cost_curve_data, axis = 0))
        write_to_excel("linux_" + instance_family_name[-2:] + "vcpu_ec2_cost_curves.xlsx", ec2_cost_curve_data)
        write_to_excel("linux_" + instance_family_name[-2:] + "vcpu_competitive_matrix.xlsx", competitive_matrix_data)

scenarios = ["windows", "windows_with_hybrid_benefit"]

for scenario in scenarios:
    for instance_family_name, instance_family in all_azure_instances.items():
        competitive_matrix_data = []
        azure_cost_curve_data = []
        dimension_cost_curve_data = []
        for instance_name, instance in instance_family.items():

            a, b = build_azure_cost_curves(instance, scenario)
            dimension_cost_curve_data.extend(a)
            azure_cost_curve_data.extend(b)

            write_to_excel(scenario + "_" + instance_family_name[-2:] + "vCPU_Dimension_Cost_Curves.xlsx", numpy.unique(dimension_cost_curve_data, axis = 0))
            write_to_excel(scenario + "_" + instance_family_name[-2:] + "vCPU_Azure_Cost_Curves.xlsx", azure_cost_curve_data)

            competitive_matrix_data.extend(build_competitive_matrix_azure(instance, scenario))
            write_to_excel(scenario + "_" + instance_family_name[-2:] + "vCPU_Competitive_Matrix_Azure.xlsx", competitive_matrix_data)
            

#ec2_instances = [[100, all_ec2_instances_windows["all_ec2_instances_windows_02"]["I3.large"]], 
#             [200, all_ec2_instances_windows["all_ec2_instances_windows_04"]["I3.xlarge"]], 
#             [300, all_ec2_instances_windows["all_ec2_instances_windows_08"]["I3.2xlarge"]], 
#             [400, all_ec2_instances_windows["all_ec2_instances_windows_16"]["I3.4xlarge"]], 
#             ]

#ec2_instances = [[100, all_ec2_instances_linux["all_ec2_instances_linux_02"]["I3.large"]], 
#             [200, all_ec2_instances_linux["all_ec2_instances_linux_04"]["I3.xlarge"]], 
#             [300, all_ec2_instances_linux["all_ec2_instances_linux_08"]["I3.2xlarge"]], 
#             [400, all_ec2_instances_linux["all_ec2_instances_linux_16"]["I3.4xlarge"]], 
#             ]
#ec2_instances = [[100, all_azure_instances["all_azure_instances_02"]["F2"]], 
#             [200, all_azure_instances["all_azure_instances_04"]["F4"]], 
#             [300, all_azure_instances["all_azure_instances_08"]["F8"]], 
#             [400, all_azure_instances["all_azure_instances_16"]["F16"]], 
#             ]
#ec2_instances = [[100, all_azure_instances["all_azure_instances_02"]["D2d v4"]], 
#             [200, all_azure_instances["all_azure_instances_04"]["D4d v4"]], 
#             [300, all_azure_instances["all_azure_instances_08"]["D8d v4"]], 
#             [400, all_azure_instances["all_azure_instances_16"]["D16d v4"]], 
#             ]
#ec2_instances = [[100, all_azure_instances["all_azure_instances_02"]["E2d v4"]], 
#             [200, all_azure_instances["all_azure_instances_04"]["E4d v4"]], 
#             [300, all_azure_instances["all_azure_instances_08"]["E8d v4"]], 
#             [400, all_azure_instances["all_azure_instances_16"]["E16d v4"]], 
#             ]
#ec2_instances = [[100, all_azure_instances["all_azure_instances_02"]["E2a v4"]], 
#             [200, all_azure_instances["all_azure_instances_04"]["L4s"]], 
#             [300, all_azure_instances["all_azure_instances_08"]["L8s"]], 
#             [400, all_azure_instances["all_azure_instances_16"]["L16s"]], 
#             ]

#vm_range = [150, 500, 1500]
#efficiency_matrix = []
#scenario = "windows_with_hybrid_benefit"
#for storage, instance in ec2_instances:
#    with_row = []
#    without_row = []
#    for vm in vm_range:
#        dimension_no_oversubscription = dimension_nodes["m1s_no_oversubscription"].copy()
#        dimension_no_oversubscription["vCPU"] = instance["vCPU"]
#        dimension_no_oversubscription["memory"] = instance["memory"]

#        dimension_oversubscription = dimension_nodes["m1s_oversubscription"].copy()
#        dimension_oversubscription["vCPU"] = instance["vCPU"]
#        dimension_oversubscription["memory"] = instance["memory"]
#        x, a = calculate_dimension_tco(dimension_no_oversubscription, vm)
#        #b = calculate_ec2_tco_with_blind_spot(instance, dimension_no_oversubscription, vm, storage)
#        b = calculate_azure_tco_with_blind_spot(instance, dimension_no_oversubscription, vm, storage, scenario)
        
#        p = round(math.ceil((b-a)*100/a),1)

#        x, a = calculate_dimension_tco(dimension_oversubscription, vm)
#        #b = calculate_ec2_tco_with_blind_spot(instance, dimension_oversubscription, vm, storage)
#        b = calculate_azure_tco_with_blind_spot(instance, dimension_oversubscription, vm, storage, scenario)
#        q = round(math.ceil((b-a)*100/a),1)
#        with_row.append(str(p) + "% / " + str(q) + "%")

        
#        x, a = calculate_dimension_tco(dimension_no_oversubscription, vm)
#        #b = calculate_ec2_tco_without_blind_spot(instance, dimension_no_oversubscription, vm, storage)
#        b = calculate_azure_tco_without_blind_spot(instance, dimension_no_oversubscription, vm, storage, scenario)
#        p = round(math.ceil((b-a)*100/a),1)
#        x, a = calculate_dimension_tco(dimension_oversubscription, vm)
#        #b = calculate_ec2_tco_without_blind_spot(instance, dimension_oversubscription, vm, storage)
#        b = calculate_azure_tco_without_blind_spot(instance, dimension_oversubscription, vm, storage, scenario)

#        q = round(math.ceil((b-a)*100/a),1)
#        without_row.append(str(p) + "% / " + str(q) + "%")

#    efficiency_matrix.append(with_row)
#    efficiency_matrix.append(without_row)

#write_to_excel("m1s_efficiency.xlsx", efficiency_matrix)

#efficiency_matrix = []
#for storage, instance in ec2_instances:
#    with_row = []
#    without_row = []
#    for vm in vm_range:
#        dimension_no_oversubscription = dimension_nodes["m1d_no_oversubscription"].copy()
#        dimension_no_oversubscription["vCPU"] = instance["vCPU"]
#        dimension_no_oversubscription["memory"] = instance["memory"]

#        dimension_oversubscription = dimension_nodes["m1d_oversubscription"].copy()
#        dimension_oversubscription["vCPU"] = instance["vCPU"]
#        dimension_oversubscription["memory"] = instance["memory"]
#        x, a = calculate_dimension_tco(dimension_no_oversubscription, vm)
#        #b = calculate_ec2_tco_with_blind_spot(instance, dimension_no_oversubscription, vm, storage)
#        b = calculate_azure_tco_with_blind_spot(instance, dimension_no_oversubscription, vm, storage, scenario)
#        p = round(math.ceil((b-a)*100/a),1)

#        x, a = calculate_dimension_tco(dimension_oversubscription, vm)
#        #b = calculate_ec2_tco_with_blind_spot(instance, dimension_oversubscription, vm, storage)
#        b = calculate_azure_tco_with_blind_spot(instance, dimension_oversubscription, vm, storage, scenario)
#        q = round(math.ceil((b-a)*100/a),1)
#        with_row.append(str(p) + "% / " + str(q) + "%")

        
#        x, a = calculate_dimension_tco(dimension_no_oversubscription, vm)
#        #b = calculate_ec2_tco_without_blind_spot(instance, dimension_no_oversubscription, vm, storage)
#        b = calculate_azure_tco_without_blind_spot(instance, dimension_no_oversubscription, vm, storage, scenario)
#        p = round(math.ceil((b-a)*100/a),1)
#        x, a = calculate_dimension_tco(dimension_oversubscription, vm)
#        #b = calculate_ec2_tco_without_blind_spot(instance, dimension_oversubscription, vm, storage)
#        b = calculate_azure_tco_without_blind_spot(instance, dimension_oversubscription, vm, storage, scenario)
#        q = round(math.ceil((b-a)*100/a),1)
#        without_row.append(str(p) + "% / " + str(q) + "%")

#    efficiency_matrix.append(with_row)
#    efficiency_matrix.append(without_row)

#write_to_excel("m1d_efficiency.xlsx", efficiency_matrix)