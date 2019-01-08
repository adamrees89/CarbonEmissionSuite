# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 16:54:47 2018

@author: adam.rees
"""

import unittest
import sqlite3
import os
import DBEISCarbonFactors

class test_InstanceNames(unittest.TestCase):
    
    def setUp(self):
        conn = sqlite3.connect("mydatabase.db")
        c = conn.cursor()
        
    def tearDown(self):
        os.remove("mydatabase.db")