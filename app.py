import os
import request,json
from apiKey import API_SECRET_KEY
from flask import Flask, render_template, redirect, flash,session,g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Favorite, Recipe
from forms import RegisterForm, LoginForm



CURR_USER_KEY = "curr_user"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL','postgresql:///mealhelp'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

connect_db(app)
db.create_all()

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]



@app.route('/')
def home():
    '''homepage'''

    return render_template('home.html')

@app.route('/register', methods=['GET','POSt'])
def new_user():
    '''register a new user'''
    

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('register.html', form=form)

        do_login(user)

        return redirect(f'/meal-search')
    else:
        return render_template('register.html', form=form)

@app.route('/login',methods=['GET','POST'])
def login_user():
    '''login a user'''
    

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(username, password)  
        
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(f'/users/{user.username}')

        flash('Invalid credentials.', 'danger')
    
    return render_template('login.html',form=form)

@app.route('/logout')
def logout():
    '''logout and return to home page'''

    session.pop(CURR_USER_KEY)
    flash('you have been logged out.', 'success')
    return redirect('/login')

@app.route('/users/<username>')
def user_details(username):
    '''show information about a user'''
    if not g.user:
        flash('You must be logged in to see this page.', 'danger')
        return redirect("/login")

    else:
        favorites = Favorite.query.filter(Favorite.user.username == users.id)        

        user = User.query.get_or_404(username)
    

    return render_template('users.html',user=user, favorites=favorites)

@app.route('/meal-search', methods=['GET','POST'])
def select_page():
    '''be shown a list of checkboxes and click boxes to create parameters for the meals that will be returned'''
    ingredients = request.form["ingredients"]
    diet = request.form["diet"]

 
    response = requests.get(f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&diet={diet}&number=20&apiKey={API_KEY}&addRecipeInformation=true")
    results = response.json()

    if not len(results):
        no_results = "No recipes available with those ingredients, check your spelling"
    else:
        no_results = ""
    
    if g.user:
        if g.user.recipes:
            favorited_recipes = [recipe.recipe_id for recipe in g.user.recipes]
        else:
            favorited_recipes = None
    else:
        favorited_recipes = None
        
        
    return render_template('meal-search.html',results=results,no_results=no_results,favorited_recipes=favorited_recipes)
    # else:
    #     return redirect('/meal-results')

@app.route('/meal-results')
def show_results():
    '''show the results from their search'''
    

    return render_template('meal-results.html')

@app.route('/users/<username>/delete',methods=['DELETE'])
def delete_user(username):
    '''delete a user'''
    if not g.user:
        flash('You must be logged in to see this page.', 'danger')
        return redirect("/login")
        

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect('/')