# -*- coding: utf-8 -*-
"""
Started 07/11/2018

This script connects to the
Department of Business, Environment, and Industrial Strategy (DBEIS) website,
downloads the carbon factors in the 'flat file' format, and saves the factors
in a SQLite3 file.  If the 'flat file' format is not available, the script
looks for the advanced file which contains all the data required.

Carbon factors publishing started in 2002, and the year can be changed in the
URL for the 2018 factors to get the appropiate year.

The SQLite database has separate tables for each year, and the columns are
defined in the sqlDumpFlatFile function
    
@author: adam.rees
"""

import requests
import sqlite3
import xlrd
import sys
import time
import os
import logging
from bs4 import BeautifulSoup
import wget

try:
    now = time.strftime("%c")
    Now = time.localtime()
    logging.basicConfig(filename=os.path.join("DBEISCFLog.log"),
                        level=logging.INFO)
    logging.info(f'\nDate and Time:\n {now}' 
                 '\n-------------------------------\n')
except:
    logging.critical("Error with the set-up of the logging function"
                     "Sys.exit(1), try/except block line 30-40\n")
    sys.exit(1)

class CarbonFactors(object):
    """
    This class which will contain the year, url, and carbon factors
    Each instance of the class will have its own table within the SQLite
    database
    """
    def __init__(self,year):
        #Provide the year and return a class instance
        #Set up the variables here
        try:
            int(year)
            if 2014 <= year <= Now[0]+1:
                pass
            else:
                raise ValueError("Input string was not a valid year")
        except ValueError:
            raise ValueError("Input string was not a valid number")
        
        self.year = year
        self.pageurl = (f"https://www.gov.uk/government/publications/"
        f"greenhouse-gas-reporting-conversion-factors-{year}")     
        self.downloadLink = "None"
        self.fileType = ""
        self.DownloadInfo = ""
        
        #Now we check if the URL exists, currently we print the result"
        self.UrlCheckResponse = self.urlCheck()
        if self.UrlCheckResponse == True:
            if sys.platform == "win32":
                import winshell
                logging.debug("I am working on a Windows machine!\n")
                self.downloadDir = os.path.join(winshell.personal_folder(),
                                                "CF Downloads")
            else:
                logging.debug("I am working on a Linux based system"
                      f"(Sys.platform = {sys.platform})\n")
                self.downloadDir = os.path.expanduser('~/CF Downloads')
            self.DownloadLocation = os.path.join(self.downloadDir,
                                                 f'{self.year} - '
                                                'Carbon Factors.xls')
            
            self.database = os.path.join(self.downloadDir,'Database.db')
        
            #Lets Fetch the CarbonFactor URL now with the FetchCF function
            self.FetchCFLink()
            self.downloadFile()
            self.sqlCreateTable(self.database)
            try:
                self.sqlDumpFlatFile(self.database)
            except Exception as e:
                print("Exception raised"
                      f"\nThrown Error: {e}\n")

        else:
            print(f"No Download found for {self.year}\n")
            logging.critical(f"No Download found for {self.year}\n")
            return
        
        #Create a log entry for the class instance
        logging.info("Instance of class created:\n"
                     f"Year: {self.year}\n"
                     f"Downloads Page URL: {self.pageurl}\n"
                     f"URL Check Result: {self.UrlCheckResponse}\n"
                     f"Factors Download Link: {self.downloadLink}\n"
                     "Created table within database with name: "
                     f"{self.tableName}\n"
                     f"Year: {self.year} has been downloaded and assimilated "
                     "into the database\n")
         
    def urlCheck(self):
        #This function retrives the head of the url and checks the status code
        request = requests.head(self.pageurl)
        if request.status_code == 200:
            return True
        else:
            return False

    def FetchCFLink(self):
        """
        This function provides a downloads webpage from where the carbon
        factors can be downloaded and returns self.downloadLink
        """
        
        request = requests.get(self.pageurl)
        soup = BeautifulSoup(request.text,"lxml")
        URLPrepend = 'https://www.gov.uk'
        linkList = []
        links = soup.select("a[href*=uploads]")
        
        for link in links:         
            linkList.append(link.get('href'))
        
        try:
            self.DownloadInfo = self.linkTypeFunc(linkList)
            self.downloadLink = ''.join([URLPrepend,
                                         self.DownloadInfo])             
        except Exception as e:
            logging.critical(f"\nError: {e}\n")
            self.downloadLink = "https://theuselessweb.com/"
    
    def linkTypeFunc(self,listLinks):
        """
        This subfunction is called from the FetchCF function and accepts a
        list of urls from the webpage.  The function will then look for a flat
        file first, then an advanced file, and finally an old style advanced
        file.  This subfunction returns the downloadLink and fileType variable
        to the FetchCF function.
        """
        
        substringFlatFile = "Flat"
        substringFlatFile2 = "flat"

        for entry in listLinks:
            if (entry.find(substringFlatFile) != -1 
                or entry.find(substringFlatFile2) != -1):
                Flatfile = entry
                return Flatfile
    
    def downloadFile(self):
        '''
        This function takes the download link generated in the FetchCF 
        function and attempts to download the file to the path indicated in 
        the DownloadLocation variable (which contains the name of the file
        linked to the year in question)
        '''
        try:
            fo = open(self.DownloadLocation, 'r')
            fo.close()
        except FileNotFoundError:
            try:
                os.makedirs(self.downloadDir,exist_ok=True)
                wget.download(self.downloadLink,self.DownloadLocation)
            except Exception as e:
                print(f"ERROR WITH DOWNLOAD: {e}\n")
    
    def sqlCreateTable(self,database):
        '''
        This function creates the sqlite table within the db, and nothing more
        '''
        conn = sqlite3.connect(database)
        c = conn.cursor()
        Year = str(self.year)
        self.tableName = f"Year_{Year}"
        try:
            table_sql = f"""CREATE TABLE {self.tableName} (
            id integer PRIMARY KEY,
            Scope text NOT NULL,
            Level_1 text NOT NULL,
            Level_2 text NOT NULL,
            Level_3 text NOT NULL,
            Level_4 text NOT NULL,
            ColumnText text NOT NULL,
            UOM text NOT NULL,
            GHG text NOT NULL,
            GHG_Conversion_Factor real NOT NULL)"""            
            c.execute(table_sql)            
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logging.debug("Error when creating table named: "
                         f"{self.tableName}.\nError: {e}")
            
    
    def sqlDumpFlatFile(self,database):
        """
        wb = Workbook
        ws = Worksheet
        d = Dictionary of values to be written to the SQL file (row by row)
        hd = Dictionary of heading row values
        conn = Connection to the SQLite object
        c = Cursor for the SQLite object
        """
        
        wb = xlrd.open_workbook(self.DownloadLocation)
        ws = wb.sheet_by_name("Factors by Category")
        hd = {}
        conn = sqlite3.connect(database)
        c = conn.cursor()        
        
        """
        Lets set out the columns that we want with the variable headings 'hdX'
        """
        hd1 = "Scope"
        hd2 = "Level 1"
        hd3 = "Level 2"
        hd4 = "Level 3"
        hd5 = "Level 4"
        hd6 = "Column Text"
        hd7 = "UOM"
        hd8 = "GHG"
        hd9 = "Factor"
        
        """
        Lets clear the table before we write to it to avoid duplicate 
        information
        """
        try:
            c.execute(f"DELETE FROM {self.tableName}")
            logging.debug("Deleted table data")
        except Exception as e:
            logging.info("Deleting data threw an exception, continuing,"
                         " It propably means that the database hasn't been"
                         f" created yet. Error: {e}")
            pass
        
        """
        Now lets scan the excel file for our data and write it to the sqlite
        database
        """
        
        HeaderRow = 0
        
        for row in range(0,10):
            for col in range(0,ws.ncols):
                if ws.cell(row,col).value == "Scope":
                    HeaderRow = row
                    
        ValuesRow = HeaderRow + 1
        
        for col in range(0,ws.ncols):         
            if ws.cell(HeaderRow,col).value == hd1:
                hd['hd1'] = col
            if ws.cell(HeaderRow,col).value.find(hd2) != -1:
                hd['hd2'] = col
            if ws.cell(HeaderRow,col).value.find(hd3) != -1:
                hd['hd3'] = col
            if ws.cell(HeaderRow,col).value.find(hd4) != -1:
                hd['hd4'] = col
            if ws.cell(HeaderRow,col).value.find(hd5) != -1:
                hd['hd5'] = col
            if ws.cell(HeaderRow,col).value.find(hd6) != -1:
                hd['hd6'] = col
            if ws.cell(HeaderRow,col).value == hd7:
                hd['hd7'] = col
            if ws.cell(HeaderRow,col).value == hd8:
                hd['hd8'] = col
            if ws.cell(HeaderRow,col).value.find(hd9) != -1:
                hd['hd9'] = col
            else:
                pass
        
        try:
            for row in range(ValuesRow,ws.nrows):
                d = []
                for dT,col in hd.items():
                    if ws.cell(row,col).value == "N/A":
                        d.append(0)
                    else:
                        d.append(ws.cell(row,col).value)          
                insert_sql = f"""INSERT INTO {self.tableName} (Scope, Level_1,
                Level_2, Level_3, Level_4, Columntext, UOM, GHG,
                GHG_Conversion_Factor) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                c.execute(insert_sql, d)
            conn.commit()
            conn.close()     
        except:
            conn.rollback()
            raise RuntimeError("An Error occured in the sqlDumpFlatFile "
                               "function.")

"""
Definition of the instances for testing

From 2014 onwards we have flat files, and before that advanced...
"""

if __name__ == "__main__":
    start = time.time()
    count = 0
    for i in range(2014,Now[0]+1):
        try:
            CarbonFactors(i)
            count = count + 1
        except:
            pass

    end = time.time()    
    print(f"Completed, I ran {count} operations.  It took"
          f" {round(end-start,2)} seconds.")