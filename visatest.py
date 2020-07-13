# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 18:00:22 2020

@author: sfrie
"""

import visa

simulator = ("C:/Users/sfrie/Box Sync/Penn_Private/Programs/Python/"
             + "Probe_Station/V3/test_environment.yaml")


# rm = visa.ResourceManager(f'{simulator}@sim')
rm = visa.ResourceManager('@sim')
instruments = rm.list_resources()

print(instruments)

source_list = [x for x in instruments if '8' in x and 'GPIB' in x]

keith = rm.open_resource(source_list[0])
