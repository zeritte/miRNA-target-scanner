from flask import Flask, Response, render_template, flash, redirect, request
from wtforms import Form, validators, TextField, BooleanField
import time
from func import dict1scrapper, dict2scrapper, dict3scrapper, dictIntersection, sorter

app = Flask(__name__)

app.secret_key = "super secret key"

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    best20 = BooleanField('Only best 20 percent?')

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    form = ReusableForm(request.form)
    print(form.errors)
    if request.method == 'POST':
        name=request.form['name']
        try:
            best20=request.form['best20']
            best20 = "1"
        except:
            best20 = "0"
    if form.validate():
        return redirect("/results/%s/%s" %(best20, name))
    else:
        flash('enter a miRNA name')
    return render_template('hello.html', form=form)

@app.route("/results/<best20>/<name>")
def results(best20, name):
    start = time.time()
    desiredMRNA = name
    best20 = int(best20)
    list1 = dict1scrapper(desiredMRNA, best20)
    list2 = dict2scrapper(desiredMRNA, best20)
    list3 = dict3scrapper(desiredMRNA, best20)
    listIntersection = dictIntersection(list1, list2, list3)    
    sorted_final_list = sorter(listIntersection)
    end = time.time()
    print(end - start)
    return render_template("dictprinter.html", lengthoflist=len(sorted_final_list),  data=sorted_final_list)

if __name__ == '__main__':
    app.run()
