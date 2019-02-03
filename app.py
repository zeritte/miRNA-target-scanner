from flask import Flask, render_template, flash, redirect, request
from wtforms import Form, validators, TextField
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
    return name

if __name__ == '__main__':
    app.run()
