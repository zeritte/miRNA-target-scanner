from flask import Flask, Response, render_template, flash, redirect, request, url_for
from wtforms import Form, validators, TextField, BooleanField, SelectField
from func import diana_scrapper, mirdb_scrapper, targetscan_scrapper, list_intersection, sorter

app = Flask(__name__)

app.secret_key = "super secret key"

class ReusableForm(Form):
    name = TextField('miRNA Name:', validators=[validators.required()])
    best20 = BooleanField('Only best 20 percent? ')
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
        return redirect(url_for('diana', name=name, specy=specy, best20=best20))
    else:
        flash('enter a miRNA name')
    return render_template('hello.html', form=form)

@app.route('/diana')
def diana():
    global diana_list
    desiredMRNA = request.args.get('name')
    best20 = int(request.args.get('best20'))
    specy = request.args.get('specy')
    diana_list = diana_scrapper(desiredMRNA, best20, specy)
    if diana_list=="error":
        return render_template("error.html", error="diana threw an error")

    return redirect(url_for('mirdb', name=desiredMRNA, specy=specy, best20=best20))

@app.route('/mirdb')
def mirdb():
    global mirdb_list
    desiredMRNA = request.args.get('name')
    best20 = int(request.args.get('best20'))
    specy = request.args.get('specy')
    mirdb_list = mirdb_scrapper(desiredMRNA, best20, specy)

    if mirdb_list=="error":
        return render_template("error.html", error="mirdb threw an error")

    return redirect(url_for('targetscan', name=desiredMRNA, specy=specy, best20=best20))

@app.route('/targetscan')
def targetscan():
    global targetscan_list
    desiredMRNA = request.args.get('name')
    best20 = int(request.args.get('best20'))
    specy = request.args.get('specy')
    targetscan_list = targetscan_scrapper(desiredMRNA, best20, specy)

    if targetscan_list=="error":
        return render_template("error.html", error="mirdb threw an error")

    return redirect(url_for('results', name=desiredMRNA, specy=specy, best20=best20))

@app.route('/results')
def results():
    intersection = list_intersection(diana_list, mirdb_list, targetscan_list)
    intersection = sorter(intersection)

    return render_template("dictprinter.html", data=intersection, lengthoflist=len(intersection))


if __name__ == '__main__':
    app.run()
