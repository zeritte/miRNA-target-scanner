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

@app.route("/results/<name>")
def results(name):
    desiredMRNA = name
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
            print(geneID, targetScore)
            dict1[geneID] = targetScore
    
    return render_template("dictprinter.html", lengthoflist=len(dict1),  data=dict1)

if __name__ == '__main__':
    app.run()
