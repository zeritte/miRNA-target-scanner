from flask import Flask, Response, render_template, flash, redirect, request, url_for
from wtforms import Form, validators, TextField, BooleanField, SelectField
from func import diana_scrapper, mirdb_scrapper, targetscan_scrapper, list_intersection, sorter
from holder import holder

app = Flask(__name__)

app.secret_key = "super secret key"

data = holder()

class ReusableForm(Form):
    name = TextField('miRNA Name:', validators=[validators.required()])
    best20 = BooleanField('Only best 20 percent? ')
    specy = SelectField('Species: ', choices = [('mouse','Mouse'),('human','Human')])


@app.route("/", methods=['GET', 'POST'])
def hello_world():
    form = ReusableForm(request.form)
    if request.method == 'POST':
        name=request.form['name']
        try:
            best20=request.form['best20']
            best20 = "1"
        except:
            best20 = "0"
        specy=request.form['specy']
    if form.validate():
        return redirect(url_for('diana', name=name, best20=best20, specy=specy))
    else:
        flash('enter a miRNA name')

    return render_template('hello.html', form=form)

@app.route('/diana/<name>/<specy>/<best20>')
def diana(name, specy, best20):
    try:
        diana_list = diana_scrapper(name, best20, specy)

        if diana_list=="error":
            return render_template("error.html", error="diana threw an error, please check your miRNA name")

        data.diana_list = diana_list
        return render_template('dianasearchdone.html', name=name, best20=best20, specy=specy, data=diana_list )
    except:
        return render_template("error.html", error="there is a server error")

@app.route('/mirdb/<name>/<specy>/<best20>')
def mirdb(name, specy, best20):
    try:
        mirdb_list = mirdb_scrapper(name, best20, specy)
        if mirdb_list=="error":
            return render_template("error.html", error="mirdb threw an error, please check your miRNA name")

        data.mirdb_list = mirdb_list
        return render_template('mirdbsearchdone.html', name=name, best20=best20, specy=specy, data=mirdb_list)
    except:
        return render_template("error.html", error="there is a server error")

@app.route('/targetscan/<name>/<specy>/<best20>')
def targetscan(name, specy, best20):
    try:
        targetscan_list = targetscan_scrapper(name, best20, specy)

        if targetscan_list=="error":
            return render_template("error.html", error="targetscan threw an error, please check your miRNA name")

        data.targetscan_list = targetscan_list
        return render_template('targetscansearchdone.html', name=name, best20=best20, specy=specy, data=targetscan_list)
    except:
        return render_template("error.html", error="there is a server error")

@app.route('/results/<name>/<specy>/<best20>')
def results(name, specy, best20):
    try:
        print(len(data.diana_list),len(data.mirdb_list),len(data.targetscan_list))
        intersection = list_intersection(data.diana_list, data.mirdb_list, data.targetscan_list)
        data.final = sorter(intersection)

        return render_template("dictprinter.html", data=data.final, lengthoflist=len(data.final))
    except:
        return render_template("error.html", error="there is a server error")


if __name__ == '__main__':
    app.debug = True
    app.run()
