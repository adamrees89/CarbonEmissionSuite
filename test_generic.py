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

    def test_new_flat_class_creation(self):
        try:
            #Create a class for a year which has a flat file format.
            DBEISCarbonFactors.CarbonFactors(2018)
        except Exception as e:
            self.fail("Cannot create CarbonFactors instance with "
                      f"modern flat file format.  Error: {e}")

    def test_old_flat_class_creation(self):
        try:
            #Create a class for a year which has an older flat file format.
            DBEISCarbonFactors.CarbonFactors(2014)
        except Exception as e:
            self.fail("Cannot create CarbonFactors instance with "
                      f"older flat file format.  Error: {e}")

    def test_non_flat_file_class_creation(self):
        try:
            #New we are going to create a class with an advanced file format
            DBEISCarbonFactors.CarbonFactors(2012)
        except Exception as e:
            self.fail("Cannot create CarbonFactors instance with "
                      f"advanced file format.  Error: {e}")

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