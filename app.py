import os
import requests,json
from key import API_SECRET_KEY
from flask import Flask, render_template, request, jsonify, redirect, flash,session,g
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

@app.route('/register', methods=['GET','POST'])
def new_user():
    '''register a new user'''
    

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user = User.register(
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

        return redirect('/')
        flash('Thank you for signing up', 'success')
    else:
        return render_template('register.html', form=form)

@app.route('/login',methods=['GET','POST'])
def login_user():
    '''login a user'''
    

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data)  
        
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect('/')

        flash('Invalid credentials.', 'danger')
    
    return render_template('login.html',form=form)

@app.route('/logout')
def logout():
    '''logout and return to home page'''

    session.pop(CURR_USER_KEY)
    flash('you have been logged out.', 'success')
    return redirect('/login')

@app.route('/user')
def user_details():
    '''show information about a user'''
    if not g.user:
        flash('You must be logged in to see this page.', 'danger')
        return redirect("/login")

    else:
        favorites = Favorite.query.filter(Favorite.user_id == g.user.id)  
        favorites_list = [ favorites.recipe_id for favorite in favorites]
        # ordered_favorites = [Recipe.query.get(id) for id in ordered_recipe_ids]

    

    return render_template('users.html',favorites=favorites_list)

@app.route('/favorites/<int:meal_id>', methods=['POST'])
def add_favorites(meal_id):
    '''allow users to add a favorite recipe'''
    if not g.user:
        flash('You must be logged to see your favorites.', 'danger')
        return redirect("/login")

    if not Recipe.query.get(meal_id):
        response = requests.get(f"https://api.spoonacular.com/recipes/{meal_id}/information?includeNutrition=true&apiKey={API_SECRET_KEY}")
        meal = response.json()
        new_recipe = Recipe(recipe_id = meal_id, title = meal["title"], image= meal["image"])
        db.session.add(new_recipe)
        db.session.commit()

    new_favorite = Favorite(user_id=g.user.id, recipe_id=meal_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(message="Meal added to Favorites")
@app.route('/meal-search',methods=['GET'])
def ingredients_search():
    return render_template('meal-search.html')

@app.route('/meal-search', methods=['POST'])
def select_page():
    '''be shown a list of checkboxes and click boxes to create parameters for the meals that will be returned'''
    ingredients = request.form["ingredients"]
    diet = request.form["diet"]

 
    # response = requests.get(f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&diet={diet}&number=20&apiKey={API_SECRET_KEY}&addRecipeInformation=true")
    response = requests.get(f"https://api.spoonacular.com/recipes/findByIngredients?apiKey={API_SECRET_KEY}&ingredients={ingredients}&diet={diet}&number=20&addRecipeInformation=true")
    results = response.json()

    if not len(results):
        no_results = "No results found."
    else:
        no_results = ""
    
    if g.user:
        if g.user.recipes:
            favorited_recipes = [recipe.recipe_id for recipe in g.user.recipes]
        else:
            favorited_recipes = None
    else:
        favorited_recipes = None
        
        
    return redirect('meal-results.html')
    
@app.route('/meal-results', methods=['GET'])
def show_meals():
    '''show the information for a specific meal'''
    response = requests.get(f"https://api.spoonacular.com/recipes/{dish_id}/information?&apiKey={API_SECRET_KEY}")
    dish = response.json()
   

    if dish["analyzedInstructions"]:
        for step in dish["analyzedInstructions"]:
            steps = [ e["step"] for e in step["steps"] ] 

    else:
        steps = []

    list = data["results"]
    results = [e for e in list]
    
    if not len(results):
        no_results = "No results found."
    else:
        no_results = ""
    
    if g.user:
        if g.user.recipes:
            favorited_recipes = [recipe.recipe_id for recipe in g.user.recipes]
        else:
            favorited_recipes = None
    else: 
        favorited_recipes = None

    return render_template("meal-results.html", results = results, no_results= no_results, favorited_recipes = favorited_recipes)


@app.route('/meal-results', methods=['POST'])
def show_results():
    '''show the results from their search'''
    response = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={dish}&diet={diet}&addRecipeInformation=true&apiKey={API_SECRET_KEY}")
    data = response.json()
  
    list = data["results"]
    results = [e for e in list]

    if not len(results):
        no_results = "No recipes available with that name, check your spelling"
    else:
        no_results = ""
    
    if g.user:
        if g.user.recipes:
            favorited_recipes = [recipe.recipe_id for recipe in g.user.recipes]
        else:
            favorited_recipes = None
    else:
        favorited_recipes = None
        
    return render_template("meal-results.html", results = results, no_results= no_results, favorited_recipes = favorited_recipes)

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