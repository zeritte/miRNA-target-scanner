from flask import Flask, render_template, flash, redirect, request
from wtforms import Form, validators, TextField
from selenium import webdriver
import csv, os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
app = Flask(__name__)

app.secret_key = "super secret key"

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
    driver = webdriver.PhantomJS()
    #scraping data1
    driver.get("http://diana.imis.athena-innovation.gr/DianaTools/index.php?r=MicroT_CDS/index")
    searchBox = driver.find_element_by_name("keywords")
    searchBox.send_keys(desiredMRNA)
    searchBox.send_keys(Keys.RETURN)
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'download_results_link')))
    download_link = driver.find_element_by_id('download_results_link').get_attribute('href')
    response = pd.read_csv(download_link)

    #cleaning data1
    dict1 = dict()
    for i in range(len(response)):
        if not response['Transcript Id'][i].startswith('UTR'):
            geneID = response['Gene Id(name)'][i]
            geneID = geneID[geneID.find("(")+1:geneID.find(")")]
            targetScore = response['miTG score'][i]
            dict1[geneID] = targetScore
    
    return dict1

def dict2scrapper(desiredMRNA):
    driver = webdriver.PhantomJS()
    #scraping data2
    driver.get("http://mirdb.org/cgi-bin/search.cgi")
    driver.find_element_by_xpath('//*[@id="table1"]/tbody/tr[2]/td/form/p/select/option[2]').click()
    searchBox = driver.find_element_by_name("searchBox")
    searchBox.send_keys(desiredMRNA)
    driver.find_element_by_xpath('//*[@id="table1"]/tbody/tr[2]/td/form/p/input[2]').click()
    table = driver.find_element_by_css_selector("#table1")

    #cleaning data2
    dict2 = dict()
    for row in table.find_elements_by_css_selector('tr'):
        geneID = [d.text for d in row.find_elements_by_css_selector('td')][4]
        if geneID == 'Gene Symbol':
            continue
        targetScore = float([d.text for d in row.find_elements_by_css_selector('td')][2])/100
        dict2[geneID] = targetScore
    
    return dict2

def dictIntersection(dict1, dict2):
    final_dict = dict()
    for element in dict1:
        if element in dict2:
            value1 = float(dict1[element])
            value2 = float(dict2[element])
            final_dict[element] = float((value1+value2)/2)
        
    return final_dict

@app.route("/results/<name>")
def results(name):
    desiredMRNA = name
    
    dict1 = dict1scrapper(desiredMRNA)
    dict2 = dict2scrapper(desiredMRNA)

    dictt = dictIntersection(dict1, dict2)
    
    return render_template("dictprinter.html", lengthoflist=len(dictt),  data=dictt)

if __name__ == '__main__':
    app.run()
