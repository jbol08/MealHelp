from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()



def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    '''users table'''

    __tablename__ = "users"
    
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    recipes = db.relationship('Recipe',secondary="favorites")

    @classmethod
    def register(cls,username,password,email,first_name,last_name):

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        user =  cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)
        db.session.add(user)

        return user

    @classmethod
    def authenticate(cls, username, password):

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            
            return user
        else:
            return False
class Favorite(db.Model):
    '''table with recipes that have been favorited and which users have favorited it'''

    __tablename__ = "favorites"

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))



class Recipe(db.Model):
    '''recipe that was favorited table'''

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.Text,nullable=False)
    image = db.Column(db.Text,nullable=False)
    # details = db.Column(db.Text,nullable=False)
    # total_time = db.Column(db.Integer, nullable=False)
   
    # favorites = db.relationship('Favorite',backref='recipe', cascade='all,delete')