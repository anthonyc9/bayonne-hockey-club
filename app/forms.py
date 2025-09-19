from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class BulkImportForm(FlaskForm):
    csv_file = FileField('CSV File', validators=[FileRequired()])
    submit = SubmitField('Import Players')

class DeletePlayerForm(FlaskForm):
    submit = SubmitField('Delete Player')

class BulkActionForm(FlaskForm):
    action = StringField('Action', validators=[DataRequired()])
    player_ids = StringField('Player IDs')
    submit = SubmitField('Submit')


