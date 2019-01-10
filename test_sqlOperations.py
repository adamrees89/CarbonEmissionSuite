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
        self.year = 2018
        pass

    def test_create_sql_database(self):
        try:
            DBEISCarbonFactors.CarbonFactors.sqlCreateTable(
                    self, "mydatabase.db")
        except Exception as e:
            self.fail(f"\nFailed to create SQLite3 database. Error: {e}")

    def tearDown(self):
        os.remove("mydatabase.db")


if __name__=='__main__':
    unittest.main()
