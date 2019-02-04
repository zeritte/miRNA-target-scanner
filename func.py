from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv, os
import pandas as pd
from bs4 import BeautifulSoup

driver = webdriver.PhantomJS()

def dict1scrapper(desiredMRNA, best20):
    print('dict1 has been started to scan')
    #scraping data1
    driver.get("http://diana.imis.athena-innovation.gr/DianaTools/index.php?r=MicroT_CDS/index")
    searchBox = driver.find_element_by_name("keywords")
    searchBox.send_keys(desiredMRNA)
    searchBox.send_keys(Keys.RETURN)
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'download_results_link')))
    download_link = driver.find_element_by_id('download_results_link').get_attribute('href')
    response = pd.read_csv(download_link)

    #cleaning data1
    tempdict = dict()
    tempdict_sorted = dict()
    returndict = dict()
    for i in range(len(response)):
        if not response['Transcript Id'][i].startswith('UTR'):
            geneID = response['Gene Id(name)'][i]
            geneID = geneID[geneID.find("(")+1:geneID.find(")")]
            targetScore = response['miTG score'][i]
            tempdict[geneID] = targetScore
    
    #best20 arranger
    if best20:
        tempdict_sorted = sorter(tempdict)
        i=0
        for element in tempdict_sorted:
            returndict[element] = tempdict_sorted[element]
            i+=1
            if(i>=len(tempdict_sorted)/5):
                break
    if not best20:
        returndict = tempdict

    return returndict

def dict2scrapper(desiredMRNA, best20):
    print('dict2 has been started to scan')
    #scraping data2
    driver.get("http://mirdb.org/cgi-bin/search.cgi")
    driver.find_element_by_xpath('//*[@id="table1"]/tbody/tr[2]/td/form/p/select/option[2]').click()
    searchBox = driver.find_element_by_name("searchBox")
    searchBox.send_keys(desiredMRNA)
    driver.find_element_by_xpath('//*[@id="table1"]/tbody/tr[2]/td/form/p/input[2]').click()
    
    #cleaning data2
    tempdict = dict()
    tempdict_sorted = dict()
    returndict = dict()
    soup = BeautifulSoup(driver.page_source, 'lxml')
    tables = soup.findChildren('table')
    my_table = tables[1]
    rows = my_table.findChildren('tr')
    for row in rows:
        cells = row.findChildren('td')
        geneID = cells[4].string
        if geneID == 'Gene Symbol':
            continue
        geneID = geneID[1:]
        targetScore = float(float(cells[2].string)/100)
        tempdict[geneID] = targetScore

    #best20 arranger
    if best20:
        tempdict_sorted = sorter(tempdict)
        i=0
        for element in tempdict_sorted:
            returndict[element] = tempdict_sorted[element]
            i+=1
            if(i>=len(tempdict_sorted)/5):
                break
    if not best20:
        returndict = tempdict
        
    return returndict

def dict3scrapper(desiredMRNA, best20):
    print('dict3 has been started to scan')
    #scraping data3
    driver.get("http://www.targetscan.org/mmu_72/")
    searchBox = driver.find_element_by_id('mirg_name')
    searchBox.send_keys(desiredMRNA)
    element = driver.find_element_by_xpath('/html/body/form/li[5]/input[2]')
    element.location_once_scrolled_into_view
    driver.find_element_by_xpath('/html/body/form/li[5]/input[2]').click()
    driver.find_element_by_css_selector('body > form:nth-child(4) > a:nth-child(2)').click() 
    download_link = driver.find_element_by_css_selector('body > a:nth-child(3)').get_attribute('href')
    data3 = pd.read_excel(download_link)

    #best20 case
    if best20:
        tempdict = dict()
        tempdict_sorted = dict()
        returndict = dict()
        for i in range(len(data3)): # normalization is not done here
            try:
                float(data3['Cumulative weighted context++ score'][i])
                geneID = data3['Target gene'][i].lower().capitalize()
                if float(data3['Cumulative weighted context++ score'][i]) != 0:
                    targetScore = -1*float(data3['Cumulative weighted context++ score'][i])
                else:
                    targetScore = 0.0
                tempdict[geneID]=targetScore
            except:
                continue

        tempdict_sorted = sorter(tempdict)
        max = list(tempdict_sorted.values())[0]
        min = list(tempdict_sorted.values())[int(len(tempdict_sorted)/5)-1]

        i=0
        for element in tempdict_sorted: #normalization is done here
            returndict[element] = (tempdict_sorted[element]-min)/(max-min)
            i+=1
            if(i>=len(tempdict_sorted)/5):
                break

    #not best20 case
    if not best20:
        returndict = dict()
        min = 1
        max = 0
        for i in range(len(data3)):
            try:
                float(data3['Cumulative weighted context++ score'][i])
                if float(data3['Cumulative weighted context++ score'][i]) != 0:
                    targetScore = -1*float(data3['Cumulative weighted context++ score'][i])
                else:
                    targetScore = 0.0
                if targetScore < min:
                    min = targetScore
                if targetScore > max:
                    max = targetScore
            except:
                continue

        for i in range(len(data3)):
            try:
                float(data3['Cumulative weighted context++ score'][i])
                geneID = data3['Target gene'][i].lower().capitalize()
                if float(data3['Cumulative weighted context++ score'][i]) != 0:
                    targetScore = -1*float(data3['Cumulative weighted context++ score'][i])
                else:
                    targetScore = 0.0
                targetScore = (targetScore-min)/(max-min)
                returndict[geneID]=targetScore
            except:
                continue
        
    return returndict

def dictIntersection(dict1, dict2, dict3):
    print("intersection has been started")
    final_dict = dict()
    for element in dict1:
        if element in dict2:
            if element in dict3:
                value1 = float(dict1[element])
                value2 = float(dict2[element])
                value3 = float(dict3[element])
                final_dict[element] = float((value1+value2+value3)/3)
        
    return final_dict

def sorter(any_dict):
    sorted_dict = dict()
    for w in sorted(any_dict, key=any_dict.get, reverse=True):
        sorted_dict[w] = any_dict[w]
    return sorted_dict