from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, DateField, SelectField, BooleanField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Email, NumberRange, Regexp
from datetime import datetime

class PlayerForm(FlaskForm):
    # Basic Player Information
    season = StringField('Season', default=str(datetime.now().year), validators=[Optional(), Length(max=10)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=50)])
    birth_year = StringField('Birth Year', validators=[Optional(), Length(max=10)])
    
    # Team and Position
    team = SelectField('Team', choices=[
        ('', 'Select Team'),
        ('8U', '8U'),
        ('10U', '10U'),
        ('12U', '12U'),
        ('14U', '14U'),
        ('16U', '16U'),
        ('18U', '18U'),
        ('Mite', 'Mite'),
        ('Squirt', 'Squirt'),
        ('Peewee', 'Peewee'),
        ('Bantam', 'Bantam'),
        ('Midget', 'Midget'),
        ('Learn to Play', 'Learn to Play')
    ], validators=[Optional()])
    
    position = SelectField('Position', choices=[
        ('', 'Select Position'),
        ('Forward', 'Forward'),
        ('Defense', 'Defense'),
        ('Goalie', 'Goalie'),
        ('Center', 'Center'),
        ('Left Wing', 'Left Wing'),
        ('Right Wing', 'Right Wing')
    ], validators=[Optional()])
    
    # Jersey and Equipment
    jersey_number = StringField('Jersey Number', validators=[Optional(), Length(max=10)])
    jersey_size = StringField('Jersey Size', validators=[Optional(), Length(max=10)])
    
    socks = StringField('Socks Size', validators=[Optional(), Length(max=10)])
    
    jacket = StringField('Jacket Size', validators=[Optional(), Length(max=10)])
    
    usa_hockey_number = StringField('USA Hockey Number', validators=[Optional(), Length(max=20)])
    
    # Father Information
    dad_first_name = StringField('Father\'s First Name', validators=[Optional(), Length(max=50)])
    dad_last_name = StringField('Father\'s Last Name', validators=[Optional(), Length(max=50)])
    dad_phone = StringField('Father\'s Phone', validators=[Optional(), Length(max=20)])
    dad_email = StringField('Father\'s Email', validators=[Optional(), Email(), Length(max=120)])
    
    # Mother Information
    mom_first_name = StringField('Mother\'s First Name', validators=[Optional(), Length(max=50)])
    mom_last_name = StringField('Mother\'s Last Name', validators=[Optional(), Length(max=50)])
    mom_phone = StringField('Mother\'s Phone', validators=[Optional(), Length(max=20)])
    mom_email = StringField('Mother\'s Email', validators=[Optional(), Email(), Length(max=120)])
    
    # Address Information
    address = StringField('Street Address', validators=[Optional(), Length(max=100)])
    city = StringField('City', validators=[Optional(), Length(max=50)])
    state = StringField('State', validators=[Optional(), Length(max=2)])
    zip_code = StringField('Zip Code', validators=[
        Optional(),
        Regexp(r'^\d{5}(-\d{4})?$', message="Invalid zip code format")
    ])
    
    # Financial Information
    paid_tuition = BooleanField('Tuition Paid in Full')
    total_tuition_amount = FloatField('Total Tuition Amount ($)', validators=[Optional(), NumberRange(min=0)])
    amount_paid = FloatField('Amount Paid ($)', validators=[Optional(), NumberRange(min=0)])
    
    # Documentation and Legal
    signed_waiver = BooleanField('Waiver Signed')
    birth_certificate = BooleanField('Birth Certificate on File')
    
    # File Upload for Documents
    document_upload = FileField('Upload Document (Birth Certificate, etc.)', validators=[
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'], 'Only PDF, image, and document files allowed!')
    ])
    
    # Legacy fields for backward compatibility
    date_of_birth = DateField('Date of Birth (Legacy)', validators=[Optional()])
    guardian_first_name = StringField('Guardian First Name (Legacy)', validators=[Optional(), Length(max=50)])
    guardian_last_name = StringField('Guardian Last Name (Legacy)', validators=[Optional(), Length(max=50)])
    paid = BooleanField('Payment Received (Legacy)')