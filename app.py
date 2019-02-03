from flask import Flask
app = Flask(__name__)

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])

@app.route('/')
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
