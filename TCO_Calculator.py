from dimension_nodes import dimension_nodes
from linux_ec2_instances import *
from windows_ec2_instances import *
from dimension import calculate_dimension_tco
from ec2 import calculate_ec2_tco_with_blind_spot, calculate_ec2_tco_without_blind_spot

import xlsxwriter
import numpy
import math


storage_start = 00
storage_end = 1100
storage_increment = 100

vm_start = 50
vm_end = 2050
vm_increment = 50



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
            for number_of_vms in range(vm_start, vm_end, vm_increment):
                racks, dimension_tco = calculate_dimension_tco(dimension, number_of_vms)
                dimension_cost_curve.append(str(round(dimension_tco/number_of_vms, 2)))

            all_dimension_cost_curves.append(dimension_cost_curve)

            for storage in range(storage_start, storage_end, storage_increment):
                ec2_cost_curve = []
                ec2_cost_curve.append(dimension["alias"] + "_" + instance["name"] + "_" + str(storage) + "_" + blind_cost)
                for number_of_vms in range(vm_start, vm_end, vm_increment):

                    ec2_tco_per_vm = calculate_ec2_tco_with_blind_spot(instance, dimension, number_of_vms, storage) / number_of_vms if blind_cost_flag else calculate_ec2_tco_without_blind_spot(instance, dimension, number_of_vms, storage) / number_of_vms
                    ec2_cost_curve.append(round(ec2_tco_per_vm,2))

                all_ec2_cost_curves.append(ec2_cost_curve)

    return all_dimension_cost_curves, all_ec2_cost_curves

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

            for storage in range(storage_start, storage_end, storage_increment):
                for number_of_vms in range(vm_start, vm_end, vm_increment):

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
        for storage in range(storage_start, storage_end, storage_increment):
            temp = []
            for j in range(0, len(competitive_matrix), 1):
                temp.append(competitive_matrix[j][i])
            i = i + 1
            transformed_competitive_matrix.append([str(storage) + " Gb"] + temp)

    instance_name_with = [instance["name"] +  " with blind cost"] + titles
    instance_name_without = [instance["name"] +  " without blind cost"] + titles
        
    length = len(list(range(storage_start, storage_end, storage_increment)))

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
dimension_cost_curve_data = []
competitive_matrix_data = []

for instance_name, instance in all_ec2_instances_windows_32.items():

    a, b = build_ec2_cost_curves(instance)
    dimension_cost_curve_data.extend(a)
    ec2_cost_curve_data.extend(b)
    
    competitive_matrix_data.extend(build_competitive_matrix(instance))

    write_to_excel("Windows_32vCPU_Dimension_Cost_Curves.xlsx", numpy.unique(dimension_cost_curve_data, axis = 0))
    write_to_excel("Windows_32vCPU_EC2_Cost_Curves.xlsx", ec2_cost_curve_data)
    write_to_excel("Windows_32vCPU_Competitive_Matrix.xlsx", competitive_matrix_data)