from flask import Flask, Response, render_template, flash, redirect, request
from wtforms import Form, validators, TextField, BooleanField, SelectField
import time
from func import diana_scrapper, mirdb_scrapper, targetscan_scrapper, list_intersection, sorter

app = Flask(__name__)

app.secret_key = "super secret key"

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    best20 = BooleanField('Only best 20 percent?: ')
    specy = SelectField('Species: ', choices = [('mouse','Mouse'),('human','Human')])

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
        specy=request.form['specy']
    if form.validate():
        return redirect("/results/%s/%s/%s" %(specy, name, best20))
    else:
        flash('enter a miRNA name')
    return render_template('hello.html', form=form)

@app.route("/results/<specy>/<name>/<best20>")
def results(specy, name, best20):
    start = time.time()
    desiredMRNA = name
    best20 = int(best20)
    diana = diana_scrapper(desiredMRNA, best20, specy)
    if diana=="error":
        return render_template("error.html", error="diana threw an error")
    mirdb = mirdb_scrapper(desiredMRNA, best20, specy)
    if mirdb=="error":
        return render_template("error.html", error="mirdb threw an error")
    targetscan = targetscan_scrapper(desiredMRNA, best20, specy)
    if targetscan=="error":
        return render_template("error.html", error="targetscan threw an error")
    listIntersection = list_intersection(diana, mirdb, targetscan)    
    sorted_final_list = sorter(listIntersection)
    end = time.time()
    print(end - start)
    
    return render_template("dictprinter.html", lengthoflist=len(sorted_final_list),  data=sorted_final_list)

if __name__ == '__main__':
    app.run()
