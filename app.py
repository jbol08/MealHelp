from flask import Flask, render_template, redirect,flash,session
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized
from models import db, connect_db, User, Favorite, Recipe
from forms import RegisterForm, LoginForm, MealForm, 


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'asfdsfds'

connect_db(app)
db.create_all()

@app.route('/')
def home():
    '''homepage'''

    return render_template('home.html')

@app.route('/register', methods=['GET','POSt'])
def new_user():
    '''register a new user'''
    form = RegisterForm()

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username,password, email, first_name,last_name)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect(f'/users/{user.username}')
    else:
        return render_template('register.html', form=form)

@app.route('/login',methods=['GET','POST'])
def login_user():
    '''login a user'''
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        
        user = User.authenticate(username, password)  
        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ["Invalid username/password."]
            return render_template('login.html',form=form)
    
    return render_template('login.html',form=form)

@app.route('/logout')
def logout():
    '''logout and return to home page'''

    session.pop('username')
    return redirect('/')

@app.route('/users/<username>')
def user_details(username):
    '''show information about a user'''
    if "username" not in session or username != session['username']:
        raise Unauthorized('must be logged in to view this page')

    if 'username' not in session or username != ['username']:
        flash('must be logged in to view')
        

    user = User.query.get(username)
    

    return render_template('users.html',user=user,form=form)

@app.route('/meal-search', methods=['GET','POST'])
def select_page():
    '''be shown a list of checkboxes and click boxes to create parameters for the meals that will be returned'''
    if "username" not in session or username != session['username']:
        raise Unauthorized('must be logged in to view this page')
        
        return render_template('meal-search.html')
    else:
        return redirect('/meal-results')

@app.route('/meal-results')
def show_results():
    '''show the results from their search'''
    if "username" not in session or username != session['username']:
        raise Unauthorized('must be logged in to view this page')

    return render_template('meal-results.html')