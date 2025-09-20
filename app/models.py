from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets

class User(db.Model, UserMixin):
    """User Model for storing user account details."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    def generate_reset_token(self):
        """Generate a password reset token for this user."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        
        # Remove any existing tokens for this user
        PasswordResetToken.query.filter_by(user_id=self.id).delete()
        
        # Create new token
        reset_token = PasswordResetToken(
            user_id=self.id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(reset_token)
        db.session.commit()
        
        return token

class PreApprovedEmails(db.Model):
    """Model for storing pre-approved email addresses."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"PreApprovedEmail('{self.email}')"


class Player(db.Model):
    """Model for storing comprehensive player information."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Basic Player Information
    season = db.Column(db.String(10))  # e.g., "2024-25"
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    birth_year = db.Column(db.String(10))  # Year only as string
    team = db.Column(db.String(30))
    position = db.Column(db.String(30))
    
    # Jersey and Equipment Information
    jersey_number = db.Column(db.String(10))
    jersey_size = db.Column(db.String(10))
    socks = db.Column(db.String(10))
    jacket = db.Column(db.String(10))
    usa_hockey_number = db.Column(db.String(20))
    
    # Father/Dad Information
    dad_first_name = db.Column(db.String(50))
    dad_last_name = db.Column(db.String(50))
    dad_phone = db.Column(db.String(20))
    dad_email = db.Column(db.String(120))
    
    # Mother/Mom Information
    mom_first_name = db.Column(db.String(50))
    mom_last_name = db.Column(db.String(50))
    mom_phone = db.Column(db.String(20))
    mom_email = db.Column(db.String(120))
    
    # Address Information
    address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(10))
    
    # Financial Information
    paid_tuition = db.Column(db.Boolean, default=False)
    total_tuition_amount = db.Column(db.Float, default=0.0)
    amount_paid = db.Column(db.Float, default=0.0)
    
    # Documentation and Legal
    signed_waiver = db.Column(db.Boolean, default=False)
    birth_certificate = db.Column(db.Boolean, default=False)
    
    # Legacy fields for backward compatibility
    date_of_birth = db.Column(db.Date)  # Keep for existing data
    guardian_first_name = db.Column(db.String(50))  # Keep for existing data
    guardian_last_name = db.Column(db.String(50))  # Keep for existing data
    paid = db.Column(db.Boolean, default=False)  # Keep for existing data
    
    # Relationships
    documents = db.relationship('PlayerDocument', backref='player', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Player('{self.first_name} {self.last_name}', Team: {self.team})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def guardian_full_name(self):
        return f"{self.guardian_first_name} {self.guardian_last_name}"


class Folder(db.Model):
    """Model for organizing files into folders."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Folder Details
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(20), default='primary')  # Bootstrap color for folder icon
    
    # Hierarchical structure
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)
    parent = db.relationship('Folder', remote_side=[id], backref='subfolders')
    
    # User who created this folder
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('folders', lazy=True))
    
    # Relationships
    files = db.relationship('File', backref='folder', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Folder('{self.name}', User: {self.user_id})"

    @property
    def full_path(self):
        """Get the full path of the folder including parent folders."""
        if self.parent:
            return f"{self.parent.full_path}/{self.name}"
        return self.name

    @property
    def file_count(self):
        """Get total number of files in this folder and all subfolders."""
        count = len(self.files)
        for subfolder in self.subfolders:
            count += subfolder.file_count
        return count


class File(db.Model):
    """Model for storing file information."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # File Details
    name = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)  # Original filename from upload
    file_path = db.Column(db.String(500), nullable=False)  # Path to file on disk
    file_size = db.Column(db.BigInteger, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # File metadata
    is_public = db.Column(db.Boolean, default=False)  # Whether file can be accessed without login
    download_count = db.Column(db.Integer, default=0)
    
    # Relationships
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)  # Can be in root
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('files', lazy=True))

    def __repr__(self):
        return f"File('{self.original_name}', Size: {self.file_size} bytes)"

    @property
    def file_extension(self):
        """Get file extension."""
        return self.original_name.split('.')[-1].lower() if '.' in self.original_name else ''

    @property
    def formatted_size(self):
        """Get human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    @property
    def is_image(self):
        """Check if file is an image."""
        image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'}
        return self.file_extension in image_extensions

    @property
    def is_document(self):
        """Check if file is a document."""
        doc_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'}
        return self.file_extension in doc_extensions

    @property
    def icon_class(self):
        """Get Bootstrap icon class for file type."""
        ext = self.file_extension
        if self.is_image:
            return 'bi-file-earmark-image'
        elif ext in {'pdf'}:
            return 'bi-file-earmark-pdf'
        elif ext in {'doc', 'docx'}:
            return 'bi-file-earmark-word'
        elif ext in {'xls', 'xlsx'}:
            return 'bi-file-earmark-excel'
        elif ext in {'ppt', 'pptx'}:
            return 'bi-file-earmark-ppt'
        elif ext in {'txt'}:
            return 'bi-file-earmark-text'
        elif ext in {'zip', 'rar', '7z'}:
            return 'bi-file-earmark-zip'
        else:
            return 'bi-file-earmark'


class PasswordResetToken(db.Model):
    """Model for storing password reset tokens."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('reset_tokens', lazy=True))

    def is_expired(self):
        """Check if the token has expired."""
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def verify_token(token):
        """Verify and return the user for a valid token."""
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        if reset_token and not reset_token.is_expired():
            return reset_token.user
        return None

    def __repr__(self):
        return f"PasswordResetToken(User: {self.user_id}, Expires: {self.expires_at})"


class PlayerDocument(db.Model):
    """Model for storing secure player documents (birth certificates, etc.)."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Document Information
    document_type = db.Column(db.String(50), nullable=False)  # 'birth_certificate', 'waiver', etc.
    original_filename = db.Column(db.String(255), nullable=False)
    secure_filename = db.Column(db.String(255), nullable=False)  # Stored filename
    file_path = db.Column(db.String(500), nullable=False)  # Full path to file
    file_size = db.Column(db.Integer)  # Size in bytes
    mime_type = db.Column(db.String(100))
    
    # Security and Access
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    access_level = db.Column(db.String(20), default='restricted')  # 'public', 'restricted', 'admin_only'
    
    # Foreign Key
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    
    # Relationships
    uploader = db.relationship('User', backref=db.backref('uploaded_documents', lazy=True))

    def __repr__(self):
        return f"PlayerDocument('{self.document_type}' for Player: {self.player_id})"


class PracticePlan(db.Model):
    """Model for storing practice plan information."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Basic Information
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.String(50))  # e.g., "60 minutes"
    
    # Focus Areas
    primary_focus = db.Column(db.String(100), nullable=False)
    secondary_focus = db.Column(db.String(100))
    
    # Practice Structure
    warm_up = db.Column(db.Text)
    main_content = db.Column(db.Text)
    cool_down = db.Column(db.Text)
    
    # Equipment and Notes
    equipment_needed = db.Column(db.Text)
    additional_notes = db.Column(db.Text)
    
    # Review Status
    review_status = db.Column(db.String(50), default='Not Reviewed')  # Not Reviewed, Reviewed, Needs Changes
    
    # External Links
    external_links = db.Column(db.Text)  # JSON string of links
    
    # Relationships
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team = db.relationship('Team', backref=db.backref('practice_plans', lazy=True, cascade='all, delete-orphan'))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('practice_plans', lazy=True))
    
    # Attachments (many-to-many with File model)
    attachments = db.relationship('File', secondary='practice_plan_attachments', lazy='subquery',
                                backref=db.backref('practice_plans', lazy=True))
    
    # Drill pieces (one-to-many relationship)
    drill_pieces = db.relationship('DrillPiece', backref='practice_plan', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"PracticePlan('{self.title}', Team: {self.team.name}, Date: {self.date})"


class Team(db.Model):
    """Model for organizing practice plans by team."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Team Details
    name = db.Column(db.String(50), nullable=False)  # e.g., "8U", "10U", "12U"
    description = db.Column(db.Text)
    
    # User who created this team
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('teams', lazy=True))

    def __repr__(self):
        return f"Team('{self.name}')"


class DrillPiece(db.Model):
    """Model for individual drill pieces within a practice plan."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Drill Details
    time = db.Column(db.String(50), nullable=False)  # e.g., "10 minutes", "5-10 min"
    drill_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    link_attachment = db.Column(db.String(500))  # URL or file reference
    
    # Order within the practice plan
    order_index = db.Column(db.Integer, nullable=False, default=0)
    
    # Relationships
    practice_plan_id = db.Column(db.Integer, db.ForeignKey('practice_plan.id'), nullable=False)
    
    def __repr__(self):
        return f"DrillPiece('{self.drill_name}', Time: {self.time})"


# Association table for practice plan attachments
practice_plan_attachments = db.Table('practice_plan_attachments',
    db.Column('practice_plan_id', db.Integer, db.ForeignKey('practice_plan.id'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('file.id'), primary_key=True)
)


### Game Tracker Models ###

class Game(db.Model):
    """Model for storing game information."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Game Information
    game_date = db.Column(db.Date, nullable=False)
    opponent_team = db.Column(db.String(100), nullable=False)
    rink_name = db.Column(db.String(100), nullable=False)
    rink_location = db.Column(db.String(200))  # Optional: address or city
    
    # Team Information
    team_name = db.Column(db.String(50), nullable=False)  # Which Badgers team played
    
    # Game Result
    badgers_score = db.Column(db.Integer, nullable=False, default=0)
    opponent_score = db.Column(db.Integer, nullable=False, default=0)
    
    # Game Status
    game_status = db.Column(db.String(20), nullable=False, default='completed')  # scheduled, completed, cancelled
    
    # Additional Information
    notes = db.Column(db.Text)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    goals = db.relationship('Goal', backref='game', lazy=True, cascade='all, delete-orphan')
    assists = db.relationship('Assist', backref='game', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"Game('{self.team_name}' vs '{self.opponent_team}' on {self.game_date})"
    
    @property
    def result(self):
        """Get the game result as a string."""
        if self.badgers_score > self.opponent_score:
            return "Win"
        elif self.badgers_score < self.opponent_score:
            return "Loss"
        else:
            return "Tie"


class Goal(db.Model):
    """Model for storing individual goals scored."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Goal Information
    period = db.Column(db.Integer, nullable=False, default=1)  # 1, 2, 3, OT
    time_scored = db.Column(db.String(10))  # e.g., "5:30", "12:45"
    
    # Player Information
    scorer_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    
    # Game Information
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    
    # Goal Type (optional)
    goal_type = db.Column(db.String(20))  # even_strength, power_play, short_handed, empty_net
    
    # Relationships
    scorer = db.relationship('Player', backref='goals_scored', foreign_keys=[scorer_id])
    
    def __repr__(self):
        return f"Goal(Player {self.scorer_id} in Game {self.game_id})"


class Assist(db.Model):
    """Model for storing individual assists."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Assist Information
    period = db.Column(db.Integer, nullable=False, default=1)  # 1, 2, 3, OT
    time_assisted = db.Column(db.String(10))  # e.g., "5:30", "12:45"
    
    # Player Information
    assister_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    
    # Game Information
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    
    # Goal Information (which goal this assist was for)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    
    # Assist Type
    assist_type = db.Column(db.String(20), default='primary')  # primary, secondary
    
    # Relationships
    assister = db.relationship('Player', backref='assists', foreign_keys=[assister_id])
    goal = db.relationship('Goal', backref='assists')
    
    def __repr__(self):
        return f"Assist(Player {self.assister_id} for Goal {self.goal_id})"