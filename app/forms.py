from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, IntegerField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional, InputRequired
from app.models import User, Player

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


### Game Tracker Forms ###

class GameForm(FlaskForm):
    """Form for creating/editing games."""
    game_date = DateField('Game Date', validators=[DataRequired()])
    opponent_team = StringField('Opponent Team', validators=[DataRequired(), Length(max=100)])
    rink_name = StringField('Rink Name', validators=[DataRequired(), Length(max=100)])
    rink_location = StringField('Rink Location', validators=[Optional(), Length(max=200)])
    team_name = SelectField('Team', validators=[DataRequired()], choices=[])
    badgers_score = IntegerField('Badgers Score', validators=[InputRequired(), NumberRange(min=0)])
    opponent_score = IntegerField('Opponent Score', validators=[InputRequired(), NumberRange(min=0)])
    game_status = SelectField('Game Status', choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='completed')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Game')


class GameGoalForm(FlaskForm):
    """Form for adding a goal during game creation."""
    scorer_id = SelectField('Scorer', validators=[DataRequired()], choices=[])


class GameAssistForm(FlaskForm):
    """Form for adding an assist during game creation."""
    assister_id = SelectField('Assister', validators=[DataRequired()], choices=[])


class GoalForm(FlaskForm):
    """Form for adding goals to a game."""
    scorer_id = SelectField('Scorer', validators=[DataRequired()], choices=[], coerce=int)
    period = SelectField('Period', choices=[
        (1, '1st Period'),
        (2, '2nd Period'),
        (3, '3rd Period'),
        (4, 'Overtime')
    ], default=1, coerce=int)
    time_scored = StringField('Time Scored (e.g., 5:30)', validators=[Optional(), Length(max=10)])
    goal_type = SelectField('Goal Type', choices=[
        ('even_strength', 'Even Strength'),
        ('power_play', 'Power Play'),
        ('short_handed', 'Short Handed'),
        ('empty_net', 'Empty Net')
    ], default='even_strength')
    submit = SubmitField('Add Goal')


class AssistForm(FlaskForm):
    """Form for adding assists to a goal."""
    assister_id = SelectField('Assister', validators=[DataRequired()], choices=[], coerce=int)
    goal_id = HiddenField('Goal ID', validators=[DataRequired()])
    period = SelectField('Period', choices=[
        (1, '1st Period'),
        (2, '2nd Period'),
        (3, '3rd Period'),
        (4, 'Overtime')
    ], default=1, coerce=int)
    time_assisted = StringField('Time Assisted (e.g., 5:30)', validators=[Optional(), Length(max=10)])
    assist_type = SelectField('Assist Type', choices=[
        ('primary', 'Primary Assist'),
        ('secondary', 'Secondary Assist')
    ], default='primary')
    submit = SubmitField('Add Assist')


class GameFilterForm(FlaskForm):
    """Form for filtering games and statistics."""
    team_filter = SelectField('Team', choices=[('', 'All Teams')], default='')
    season_filter = SelectField('Season', choices=[('', 'All Seasons')], default='')
    date_from = DateField('From Date', validators=[Optional()])
    date_to = DateField('To Date', validators=[Optional()])
    submit = SubmitField('Filter')


class ContactForm(FlaskForm):
    """Form for creating/editing team contacts."""
    team_name = StringField('Team Name', validators=[DataRequired(), Length(max=100)])
    age_group = SelectField('Age Group', validators=[DataRequired()], choices=[
        ('8U', '8U'),
        ('10U', '10U'),
        ('12U', '12U'),
        ('14U', '14U'),
        ('16U', '16U'),
        ('18U', '18U')
    ])
    division = StringField('Division', validators=[Optional(), Length(max=50)])
    color = StringField('Color', validators=[Optional(), Length(max=50)])
    coach_full_name = StringField('Coach Full Name', validators=[Optional(), Length(max=100)])
    coach_email = StringField('Coach Email', validators=[Optional(), Email(), Length(max=120)])
    manager_full_name = StringField('Manager Full Name', validators=[Optional(), Length(max=100)])
    manager_email = StringField('Manager Email', validators=[Optional(), Email(), Length(max=120)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Contact')


class ContactFilterForm(FlaskForm):
    """Form for filtering contacts."""
    age_group_filter = SelectField('Age Group', choices=[('', 'All Age Groups')], default='')
    team_name_filter = StringField('Team Name', validators=[Optional()])
    submit = SubmitField('Filter')


class ContactBulkImportForm(FlaskForm):
    csv_file = FileField('CSV File', validators=[FileRequired()])
    submit = SubmitField('Import Contacts')


