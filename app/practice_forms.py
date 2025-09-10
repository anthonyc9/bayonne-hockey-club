from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime

class TeamForm(FlaskForm):
    """Form for creating/editing teams."""
    name = StringField('Team Name', validators=[DataRequired(), Length(min=1, max=50)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])


class DrillPieceForm(FlaskForm):
    """Form for individual drill pieces."""
    time = StringField('Time', validators=[DataRequired(), Length(max=50)], 
                      render_kw={'placeholder': 'e.g., 10 minutes, 5-10 min'})
    drill_name = StringField('Drill Name', validators=[DataRequired(), Length(max=200)],
                           render_kw={'placeholder': 'e.g., Skating Drills, Passing Practice'})
    description = TextAreaField('Description', validators=[Optional()],
                              render_kw={'rows': 3, 'placeholder': 'Describe the drill, setup, and objectives...'})
    link_attachment = StringField('Link/Attachment', validators=[Optional(), Length(max=500)],
                                render_kw={'placeholder': 'URL or file reference (optional)'})


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
    
    # Practice Structure - Dynamic Drill Pieces
    drill_pieces = FieldList(FormField(DrillPieceForm), min_entries=1, max_entries=20)
    
    def __init__(self, *args, **kwargs):
        super(PracticePlanForm, self).__init__(*args, **kwargs)
        
        # Handle drill pieces data if provided
        if 'obj' in kwargs and kwargs['obj']:
            practice_plan = kwargs['obj']
            print(f"DEBUG: Form init - practice_plan has {len(practice_plan.drill_pieces)} drill pieces")
            # Clear existing entries and populate with actual drill pieces
            self.drill_pieces.entries = []
            for drill_piece in practice_plan.drill_pieces:
                drill_data = {
                    'time': drill_piece.time,
                    'drill_name': drill_piece.drill_name,
                    'description': drill_piece.description or '',
                    'link_attachment': drill_piece.link_attachment or ''
                }
                self.drill_pieces.append_entry(drill_data)
                print(f"DEBUG: Form init - Added drill piece: {drill_data}")
        
        # Ensure at least one drill piece is always available
        if not self.drill_pieces.entries:
            self.drill_pieces.append_entry()
    
    # Legacy Practice Structure (keeping for backward compatibility)
    warm_up = TextAreaField('Warm Up', validators=[Optional(), Length(max=1000)])
    main_content = TextAreaField('Main Content', validators=[Optional(), Length(max=1000)])
    cool_down = TextAreaField('Cool Down', validators=[Optional(), Length(max=1000)])
    
    # Equipment and Notes
    equipment_needed = TextAreaField('Equipment Needed', validators=[Optional(), Length(max=500)])
    additional_notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=1000)])
    
    # External Links
    external_links = TextAreaField('External Links (one per line)', validators=[Optional(), Length(max=1000)])
    
    # File Attachments
    attachment_ids = StringField('File Attachments', validators=[Optional()])
