# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 16:54:47 2018

@author: adam.rees
"""

import unittest
import os
import DBEISCarbonFactors

class test_InstanceNames(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_create_sql_database(self):
        database = "mydatabase.db"
        try:
            DBEISCarbonFactors.sqlCreateTable(database)
        except Exception as e:
            self.fail(f"\nFailed to create SQLite3 database. Error: {e}")

    def tearDown(self):
        os.remove("mydatabase.db")