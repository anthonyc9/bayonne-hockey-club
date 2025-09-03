from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime

class TeamForm(FlaskForm):
    """Form for creating/editing teams."""
    name = StringField('Team Name', validators=[DataRequired(), Length(min=1, max=50)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])


class PracticePlanForm(FlaskForm):
    """Form for creating/editing practice plans."""
    # Basic Information
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    date = DateField('Date', validators=[DataRequired()], default=datetime.now)
    duration = StringField('Duration', validators=[Optional(), Length(max=50)])
    
    # Focus Areas
    primary_focus = SelectField('Primary Focus', choices=[
        ('', 'Select Primary Focus'),
        ('Skating', 'Skating'),
        ('Stickhandling', 'Stickhandling'),
        ('Passing', 'Passing'),
        ('Shooting', 'Shooting'),
        ('Faceoffs', 'Faceoffs'),
        ('Breakouts', 'Breakouts'),
        ('Forechecking', 'Forechecking'),
        ('Backchecking', 'Backchecking'),
        ('Power Play', 'Power Play'),
        ('Penalty Kill', 'Penalty Kill'),
        ('Goaltending', 'Goaltending'),
        ('Team Building', 'Team Building'),
        ('Conditioning', 'Conditioning'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    
    secondary_focus = SelectField('Secondary Focus', choices=[
        ('', 'Select Secondary Focus'),
        ('N/A', 'N/A'),
        ('Skating', 'Skating'),
        ('Stickhandling', 'Stickhandling'),
        ('Passing', 'Passing'),
        ('Shooting', 'Shooting'),
        ('Faceoffs', 'Faceoffs'),
        ('Breakouts', 'Breakouts'),
        ('Forechecking', 'Forechecking'),
        ('Backchecking', 'Backchecking'),
        ('Power Play', 'Power Play'),
        ('Penalty Kill', 'Penalty Kill'),
        ('Goaltending', 'Goaltending'),
        ('Team Building', 'Team Building'),
        ('Conditioning', 'Conditioning'),
        ('Other', 'Other')
    ], validators=[Optional()])
    
    # Practice Structure
    warm_up = TextAreaField('Warm Up', validators=[Optional(), Length(max=1000)])
    main_content = TextAreaField('Main Content', validators=[Optional(), Length(max=1000)])
    cool_down = TextAreaField('Cool Down', validators=[Optional(), Length(max=1000)])
    
    # Equipment and Notes
    equipment_needed = TextAreaField('Equipment Needed', validators=[Optional(), Length(max=500)])
    additional_notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=1000)])
    
    # Review Status
    review_status = SelectField('Review Status', choices=[
        ('Not Reviewed', 'Not Reviewed'),
        ('Reviewed', 'Reviewed'),
        ('Needs Changes', 'Needs Changes')
    ], default='Not Reviewed')
    
    # External Links
    external_links = TextAreaField('External Links (one per line)', validators=[Optional(), Length(max=1000)])
    
    # File Attachments
    attachment_ids = StringField('File Attachments', validators=[Optional()])
