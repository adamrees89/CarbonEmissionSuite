# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 16:06:20 2018

@author: adam.rees
"""
import unittest
import DBEISCarbonFactors

class test_InstanceNames(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_letters_for_instance_name(self):
        with self.assertRaises(ValueError):
            DBEISCarbonFactors.CarbonFactors("xxxyyyxxxyyyxxy")
    
    def test_old_year(self):
        with self.assertRaises(ValueError):
            DBEISCarbonFactors.CarbonFactors(1960)
    
    def test_future_year(self):
        with self.assertRaises(ValueError):
            DBEISCarbonFactors.CarbonFactors(2050)
        

if __name__=='__main__':
    unittest.main()