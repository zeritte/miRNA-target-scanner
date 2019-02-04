from flask import Flask, Response, render_template, flash, redirect, request
from wtforms import Form, validators, TextField
from selenium import webdriver
import csv, os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from bs4 import BeautifulSoup
app = Flask(__name__)

app.secret_key = "super secret key"

dict1 = dict()
dict2 = dict()
dict3 = dict()
final_dict = dict()
sorted_final_list = dict()
driver = webdriver.PhantomJS()

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    form = ReusableForm(request.form)
    print(form.errors)
    if request.method == 'POST':
        name=request.form['name']
        print(name)

    if form.validate():
        # Save the comment here.
        return redirect("/results/%s" %name)
    else:
        flash('enter a miRNA name')
    return render_template('hello.html', form=form)

def dict1scrapper(desiredMRNA):
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
    for i in range(len(response)):
        if not response['Transcript Id'][i].startswith('UTR'):
            geneID = response['Gene Id(name)'][i]
            geneID = geneID[geneID.find("(")+1:geneID.find(")")]
            targetScore = response['miTG score'][i]
            dict1[geneID] = targetScore
    
    return dict1

def dict2scrapper(desiredMRNA):
    print('dict2 has been started to scan')
    #scraping data2
    driver.get("http://mirdb.org/cgi-bin/search.cgi")
    driver.find_element_by_xpath('//*[@id="table1"]/tbody/tr[2]/td/form/p/select/option[2]').click()
    searchBox = driver.find_element_by_name("searchBox")
    searchBox.send_keys(desiredMRNA)
    driver.find_element_by_xpath('//*[@id="table1"]/tbody/tr[2]/td/form/p/input[2]').click()
    
    #cleaning data2
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
        dict2[geneID] = targetScore
    
    return dict2

def dict3scrapper(desiredMRNA):
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
            dict3[geneID]=targetScore
        except:
            continue

    return dict3

def dictIntersection(dict1, dict2, dict3):
    print("intersection has been started")
    for element in dict1:
        if element in dict2:
            if element in dict3:
                value1 = float(dict1[element])
                value2 = float(dict2[element])
                value3 = float(dict3[element])
                final_dict[element] = float((value1+value2+value3)/3)
        
    return final_dict

def sorter(final_dict):
    for w in sorted(final_dict, key=final_dict.get, reverse=True):
        sorted_final_list[w] = final_dict[w]

@app.route("/results/<name>")
def results(name):
    desiredMRNA = name
    dict1scrapper(desiredMRNA)
    dict2scrapper(desiredMRNA)
    dict3scrapper(desiredMRNA)
    dictIntersection(dict1, dict2, dict3)    
    sorter(final_dict)
    return render_template("dictprinter.html", lengthoflist=len(sorted_final_list),  data=sorted_final_list)

if __name__ == '__main__':
    app.run()
