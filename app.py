from flask import Flask, Response, render_template, flash, redirect, request, url_for
from wtforms import Form, validators, TextField, BooleanField, SelectField
from func import diana_scrapper, mirdb_scrapper, targetscan_scrapper, list_intersection, sorter

app = Flask(__name__)

app.secret_key = "super secret key"

global best20
global name
global specy
global diana_list
global mirdb_list
global targetscan_list

class ReusableForm(Form):
    name = TextField('miRNA Name:', validators=[validators.required()])
    best20 = BooleanField('Only best 20 percent? ')
    specy = SelectField('Species: ', choices = [('mouse','Mouse'),('human','Human')])


@app.route("/", methods=['GET', 'POST'])
def hello_world():
    form = ReusableForm(request.form)
    global best20, name, specy
    if request.method == 'POST':
        name=request.form['name']
        try:
            best20=request.form['best20']
            best20 = "1"
        except:
            best20 = "0"
        specy=request.form['specy']
    if form.validate():
        return redirect(url_for('diana'))
    else:
        flash('enter a miRNA name')

    return render_template('hello.html', form=form)

@app.route('/diana')
def diana():
    try:
        global diana_list, name, specy, best20
        local_name = name
        local_specy = specy
        local_best20 = int(best20)
        diana_list = diana_scrapper(local_name, local_best20, local_specy)

        if diana_list=="error":
            return render_template("error.html", error="diana threw an error, please check your miRNA name")

        return render_template('dianasearchdone.html')
    except:
        return render_template("error.html", error="there is a server error")

@app.route('/mirdb')
def mirdb():
    try:
        global mirdb_list, name, specy, best20
        local_name = name
        local_specy = specy
        local_best20 = int(best20)
        mirdb_list = mirdb_scrapper(local_name, local_best20, local_specy)

        if mirdb_list=="error":
            return render_template("error.html", error="mirdb threw an error, please check your miRNA name")

        return render_template('mirdbsearchdone.html')
    except:
        return render_template("error.html", error="there is a server error")

@app.route('/targetscan')
def targetscan():
    try:
        global targetscan_list, name, specy, best20
        local_name = name
        local_specy = specy
        local_best20 = int(best20)
        targetscan_list = targetscan_scrapper(local_name, local_best20, local_specy)

        if targetscan_list=="error":
            return render_template("error.html", error="targetscan threw an error, please check your miRNA name")

        return render_template('targetscansearchdone.html')
    except:
        return render_template("error.html", error="there is a server error")

@app.route('/results')
def results():
    try:
        global diana_list
        global mirdb_list
        global targetscan_list
        intersection = list_intersection(diana_list, mirdb_list, targetscan_list)
        del diana_list
        del mirdb_list
        del targetscan_list
        intersection = sorter(intersection)

        return render_template("dictprinter.html", data=intersection, lengthoflist=len(intersection))
    except:
        return render_template("error.html", error="there is a server error")


if __name__ == '__main__':
    app.debug = True
    app.run()
