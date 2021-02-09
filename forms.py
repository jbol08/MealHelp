from wtforms import StringField,PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Email, Length
from flask_wtf import FlaskForm

class RegisterForm(FlaskForm):
    '''register a user'''

    username = StringField('User Name', validators=[InputRequired(), Length(min=1, max=20)],)

    password = PasswordField('Password',validators=[InputRequired()],)

    email = StringField('Email', validators=[InputRequired(), Email(), Length(min=1, max=50)],)

    first_name = StringField('First Name', validators=[InputRequired(), Length(min=1, max=30)],)
    
    last_name = StringField('Last Name', validators=[InputRequired(), Length(min=1, max=30)],)

class LoginForm(FlaskForm):
    '''login a user'''

    username = StringField('User Name', validators=[InputRequired()],)

    password = PasswordField('Password',validators=[InputRequired()],)

class MealForm(FlaskForm):
    '''select checkboxes for meal parameters'''
    

    