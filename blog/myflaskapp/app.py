from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Shoppinglist
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Schaken1!'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MySQL
mysql = MySQL(app)

Shoppinglist = Shoppinglist()

@app.route('/')
def index():
    return render_template('home.html', shoppinglist = Shoppinglist)

#info
@app.route('/info')
def about():
    return render_template('info.html')

#register form class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

#register
@app.route('/register', methods=['GET', 'POST'] )
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create Curser
        cur= mysql.connection.cursor()

        cur.execute("INSERT INTO user(name, username , password) VALUES(%s, %s, %s)", (name, username, password))
        #commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can login', 'success')

        return redirect(url_for('index'))

    return render_template('register.html', form=form)

#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
            #get form fields
        username= request.form['username']
        password_form= request.form['password']

        #Create Curser
        cur = mysql.connection.cursor()

        result= cur.execute("SELECT * FROM user WHERE username =%s", [username])
        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            #compare passwords
            if sha256_crypt.verify(password_form, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('myshoppinglist'))

            else:
                error ='incorrect password'
                return render_template('login.html', error=error)
            cur.close
        else:
            error = "Username not found"
            return render_template('login.html', error=error)



    return render_template('login.html')

#checked if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Please login before entering this page', 'danger')
            return redirect(url_for('login'))
    return wrap


#logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# main screen once logged in
@app.route('/myshoppinglist')
@is_logged_in
def myshoppinglist():
    return render_template('myshoppinglist.html')




if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
