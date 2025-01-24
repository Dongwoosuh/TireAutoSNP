# -*- coding: utf-8 -*- 
import os
import csv
import numpy as np

from odbAccess import *

__all__ = ['bending_moment_extraction']

def bending_moment_extraction(odb_name):
    print("...Bending Moment Extraction...")
    odb = openOdb(path=odb_name, readOnly=True)
    
    step = odb.steps['bending']
    node_set_name = 'L1'
    node_set = odb.rootAssembly.nodeSets[node_set_name]
    assembly_node_label = node_set.nodes[0][0].label
    # print("Node labels: ", assembly_node_label)
    node_name = 'Node ASSEMBLY.{}'.format(assembly_node_label)
    
    try:
        history_region = step.historyRegions[node_name]  # Node PartName.nodenum
    except KeyError:
        print("History region 'Node ASSEMBLY.2' not found in odb file: {}".format(odb_name))
        
    L1_RM3 = history_region.historyOutputs['RM3'].data
    bending_moment = L1_RM3[-1][-1]
    bending_moment = abs(bending_moment)*2
    print("Bending Moment: {}\n".format(bending_moment))
    return bending_moment