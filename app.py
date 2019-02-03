from flask import Flask, render_template, flash, redirect, request
from wtforms import Form, validators, TextField
from selenium import webdriver
import csv, os, sqlite3
import urllib.request
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
    conn = sqlite3.connect( "geneDB.db" )
    conn.text_factory = str
    cur = conn.cursor()
    cur.executescript('DROP TABLE IF EXISTS table1; DROP TABLE IF EXISTS table2; DROP TABLE IF EXISTS table3') #cleaning old tables
    cur.executescript('CREATE TABLE IF NOT EXISTS table1 (id VARCHAR, value DOUBLE)')
    cur.executescript('CREATE TABLE IF NOT EXISTS table2 (id VARCHAR, value DOUBLE)')
    cur.executescript('CREATE TABLE IF NOT EXISTS table3 (id VARCHAR, value DOUBLE)')
    driver = webdriver.PhantomJS()

    #scraping data1
    driver.get("http://diana.imis.athena-innovation.gr/DianaTools/index.php?r=MicroT_CDS/index")
    searchBox = driver.find_element_by_name("keywords")
    searchBox.send_keys(desiredMRNA)
    searchBox.send_keys(Keys.RETURN)
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'download_results_link')))
    download_link = driver.find_element_by_id('download_results_link').get_attribute('href')
    urllib.request.urlretrieve(download_link, "data1.csv")

    #cleaning data1
    reader = csv.reader(open('data1.csv'))
    for row in reader:
            if row[0] != 'Transcript Id' and not row[0].startswith("UTR"):
                    field2 = row[1]
                    field4 = row[3]
                    geneID = field2[field2.find("(")+1:field2.find(")")]
                    targetScore = float(field4)
                    cur.execute('INSERT OR IGNORE INTO table1 (id, value) VALUES (?,?)', (geneID, targetScore))
                    conn.commit()
    #scraping data2
    driver.get("http://mirdb.org/cgi-bin/search.cgi")
    driver.find_element_by_xpath('//*[@id="table1"]/tbody/tr[2]/td/form/p/select/option[2]').click()
    searchBox = driver.find_element_by_name("searchBox")
    searchBox.send_keys(desiredMRNA)
    driver.find_element_by_xpath('//*[@id="table1"]/tbody/tr[2]/td/form/p/input[2]').click()
    table = driver.find_element_by_css_selector("#table1")
    with open('data2.csv', 'w', newline='') as csvfile:
            wr = csv.writer(csvfile)
            for row in table.find_elements_by_css_selector('tr'):
                    wr.writerow([d.text for d in row.find_elements_by_css_selector('td')])


    #cleaning data2
    reader = csv.reader(open('data2.csv'))
    for element in reader:  # get rid of header
            element[0]
            break
    for row in reader:
            field3 = row[2]
            field5 = row[4]
            geneID = field5
            targetScore = float(float(field3)/100)
            cur.execute('INSERT OR IGNORE INTO table2 (id, value) VALUES (?,?)', (geneID, targetScore))
            conn.commit()

    #scraping data3
    driver.get("http://www.targetscan.org/mmu_72/")
    searchBox = driver.find_element_by_id('mirg_name')
    searchBox.send_keys(desiredMRNA)
    element = driver.find_element_by_xpath('/html/body/form/li[5]/input[2]')
    element.location_once_scrolled_into_view
    driver.find_element_by_xpath('/html/body/form/li[5]/input[2]').click()
    driver.find_element_by_css_selector('body > form:nth-child(4) > a:nth-child(2)').click()
    download_link = driver.find_element_by_css_selector('body > a:nth-child(3)').get_attribute('href')
    urllib.request.urlretrieve(download_link, "data3.xlsx")
    data_xlsx = pd.read_excel('data3.xlsx')
    data_xlsx.to_csv('data3.csv', encoding='utf-8', index=False)
    os.remove("data3.xlsx")

    #cleaning data3
    normalization_reader = csv.reader(open('data3.csv'))
    reader = csv.reader(open('data3.csv'))
    max = 0
    min = 1
    cumulative_index=0
    for element in normalization_reader:
        while element[cumulative_index] != 'Cumulative weighted context++ score':
            cumulative_index+=1
        break

    for row in normalization_reader:
        try:
            if float(row[cumulative_index]) != 0:
                row[cumulative_index] = -1*float(row[cumulative_index])
            else:
                row[cumulative_index] = 0.0
            if row[cumulative_index] > max:
                max = row[cumulative_index]
            if row[cumulative_index]<min:
                min = row[cumulative_index]
        except:
            continue

    for element in reader: # get rid of header
        element[0]
        break

    for row in reader:
        try:
            field1 = row[0]
            if float(row[cumulative_index]) != 0:
                row[cumulative_index] = -1*float(row[cumulative_index])
            else:
                row[cumulative_index] = 0.0
            geneID = field1.lower()
            geneID = geneID.capitalize()
            targetScore = (row[cumulative_index]-min)/(max-min)
            cur.execute('INSERT OR IGNORE INTO table3 (id, value) VALUES (?,?)', (geneID, targetScore))
            conn.commit()
        except:
            continue

    #operations
    cur.execute('SELECT id FROM table1 WHERE EXISTS (SELECT id FROM table3 WHERE id=table1.id AND EXISTS (SELECT id FROM table2 WHERE id=table1.id))')
    concurrence = cur.fetchall()
    concurrence_id = list()
    final_list = dict()
    for element in concurrence:
     concurrence_id.append(element[0])
    for id in concurrence_id:
      cur.execute("SELECT value FROM table1 WHERE id='%s'" %id)
      value = cur.fetchall()
      value1 = value[0][0]
      cur.execute("SELECT value FROM table2 WHERE id='%s'" % id)
      value = cur.fetchall()
      value2 = value[0][0]
      cur.execute("SELECT value FROM table3 WHERE id='%s'" % id)
      value = cur.fetchall()
      value3 = value[0][0]
      avg_value = float((float(value1)+float(value2)+float(value3))/3)
      final_list[id] = avg_value

    sorted_final_list = dict()

    for w in sorted(final_list, key=final_list.get, reverse=True):
      sorted_final_list[w]=final_list[w]

    return render_template("dictprinter.html", lengthoflist=len(final_list),  data=sorted_final_list)


if __name__ == '__main__':
    app.run()
