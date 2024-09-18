#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 14:55:36 2024

@author: thoverga
"""



import sys


try:
    # sys.exit('balblabla')
    assert 1 == 2, 'kan je dit lezen?'
except Exception as e:
    print(f' exception gevonden: {e}')

except SystemExit:
    msg = sys.exc_info()[1]
    print(f' syste exit met {msg}')