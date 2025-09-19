from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, make_response, send_file
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, PreApprovedEmails, Player, Folder, File, PasswordResetToken, PlayerDocument, Team, PracticePlan, DrillPiece
from app.player_forms import PlayerForm

from app.email_utils import send_password_reset_email
from app import db, bcrypt
from datetime import datetime
from flask import current_app
import csv
from io import StringIO
import json
from werkzeug.utils import secure_filename
import os
import uuid
import traceback

# Main Blueprint
main = Blueprint('main', __name__)

### Utility Functions ###
def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_document(file, player_id, document_type='general'):
    """Save uploaded document securely."""
    if file and allowed_file(file.filename):
        # Generate secure filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        secure_name = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Create full file path
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_name)
        
        # Save file
        file.save(file_path)
        
        # Create database record
        document = PlayerDocument(
            document_type=document_type,
            original_filename=original_filename,
            secure_filename=secure_name,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            mime_type=file.content_type,
            player_id=player_id,
            uploaded_by=current_user.id
        )
        
        db.session.add(document)
        return document
    return None

### Authentication Routes ###
@main.route("/")
@main.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            flash("Login successful!", "success")
            return redirect(next_page if next_page else url_for("main.dashboard"))
        else:
            flash("Login unsuccessful. Please check email and password.", "danger")
    return render_template("login.html")

@main.route("/logout")
def logout():
    """Logs out the current user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))

@main.route("/register", methods=["GET", "POST"])
def register():
    """Handles user registration."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validate email is pre-approved
        pre_approved = PreApprovedEmails.query.filter_by(email=email).first()
        if not pre_approved:
            flash("This email is not authorized for registration. Please contact an administrator.", "danger")
            return redirect(url_for("main.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("main.register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("main.register"))

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash("This username is already taken.", "danger")
            return redirect(url_for("main.register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Your account has been created! You can now log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")

@main.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Handle password reset requests."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email").strip()
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            try:
                # Generate reset token
                token = user.generate_reset_token()
                
                # Send email
                if send_password_reset_email(user, token):
                    flash("Password reset instructions have been sent to your email.", "info")
                else:
                    flash("There was an error sending the email. Please try again or contact support.", "danger")
            except Exception as e:
                print(f"Error in password reset: {str(e)}")
                flash("There was an error processing your request. Please try again.", "danger")
        else:
            # For security, show the same message even if user doesn't exist
            flash("Password reset instructions have been sent to your email.", "info")
        
        return redirect(url_for("main.forgot_password"))

    return render_template("forgot_password.html")

@main.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Handle password reset with token."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    
    # Verify the token
    user = PasswordResetToken.verify_token(token)
    if not user:
        flash("Invalid or expired password reset token.", "danger")
        return redirect(url_for("main.forgot_password"))
    
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("reset_password.html")
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("reset_password.html")
        
        try:
            # Update user's password
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            user.password = hashed_password
            
            # Remove the used token
            PasswordResetToken.query.filter_by(token=token).delete()
            
            db.session.commit()
            
            flash("Your password has been reset successfully. You can now log in.", "success")
            return redirect(url_for("main.login"))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error resetting password: {str(e)}")
            flash("There was an error resetting your password. Please try again.", "danger")
    
    return render_template("reset_password.html")

### Dashboard Routes ###
@main.route("/dashboard")
@login_required
def dashboard():
    """Displays the user dashboard."""
    # Get counts for dashboard stats
    total_players = Player.query.count()
    team_counts = db.session.query(Player.team, db.func.count(Player.id)).group_by(Player.team).all()
    unpaid_count = Player.query.filter_by(paid=False).count()
    
    return render_template("dashboard.html", 
                         name=current_user.username,
                         total_players=total_players,
                         team_counts=team_counts,
                         unpaid_count=unpaid_count)

### Player Management Routes ###
@main.route("/roster")
@login_required
def roster():
    """Display all players."""
    from app.forms import BulkImportForm, DeletePlayerForm
    
    form = BulkImportForm()
    delete_form = DeletePlayerForm()
    
    try:
        # Get optional filter parameters
        team_filter = request.args.get('team', None)
        season_filter = request.args.get('season', None)
        payment_filter = request.args.get('paid', None)
        search = request.args.get('search', '').strip()
        
        print(f"=== ROSTER FILTER DEBUG ===")
        print(f"Team filter: '{team_filter}' (type: {type(team_filter)})")
        print(f"Season filter: '{season_filter}' (type: {type(season_filter)})")
        print(f"Payment filter: '{payment_filter}' (type: {type(payment_filter)})")
        print(f"Search: '{search}' (type: {type(search)})")

        # Start with base query
        query = Player.query
        print(f"Initial query: {query.count()} players")

        # Apply filters
        if team_filter and team_filter != '':  # Add check for empty string
            query = query.filter(Player.team == team_filter)
            print(f"After team filter '{team_filter}': {query.count()} players")
        if season_filter and season_filter != '':  # Add season filter
            query = query.filter(Player.season == season_filter)  # Keep as string
            print(f"After season filter '{season_filter}': {query.count()} players")
        if payment_filter is not None:
            query = query.filter(Player.paid == (payment_filter.lower() == 'true'))
            print(f"After payment filter '{payment_filter}': {query.count()} players")
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Player.first_name.ilike(search_term),
                    Player.last_name.ilike(search_term),
                    Player.guardian_first_name.ilike(search_term),
                    Player.guardian_last_name.ilike(search_term)
                )
            )
            print(f"After search '{search}': {query.count()} players")

        # Get sorted players
        players = query.order_by(Player.last_name, Player.first_name).all()
        print(f"Final result: {len(players)} players")
        print("=== END ROSTER FILTER DEBUG ===")

        # Get unique teams for filter dropdown (exclude empty/None values)
        teams = db.session.query(Player.team).distinct().filter(Player.team != '').filter(Player.team != None).all()
        teams = [team[0] for team in teams]

        # Get unique seasons for filter dropdown
        seasons = db.session.query(Player.season).distinct().filter(Player.season != None).order_by(Player.season.desc()).all()
        seasons = [season[0] for season in seasons]

        return render_template("roster_mobile_friendly.html", 
                             players=players,
                             teams=teams,
                             seasons=seasons,
                             current_team=team_filter,
                             current_season=season_filter,
                             current_paid=payment_filter,
                             form=form,
                             delete_form=delete_form,
                             search=search)
    except Exception as e:
        print(f"Error in roster route: {str(e)}")
        import traceback
        traceback.print_exc()
        return str(e), 500

@main.route("/roster/export")
@login_required
def export_roster():
    """Export roster to CSV."""
    try:
        # Get the same filter parameters as the roster view
        team_filter = request.args.get('team', None)
        season_filter = request.args.get('season', None)
        payment_filter = request.args.get('paid', None)
        search = request.args.get('search', '').strip()

        # Start with base query
        query = Player.query

        # Apply same filters as roster view
        if team_filter and team_filter != '':
            query = query.filter(Player.team == team_filter)
        if season_filter and season_filter != '':
            query = query.filter(Player.season == season_filter)  # Keep as string
        if payment_filter and payment_filter != '' and payment_filter != 'None':
            query = query.filter(Player.paid == (payment_filter.lower() == 'true'))
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Player.first_name.ilike(search_term),
                    Player.last_name.ilike(search_term),
                    Player.guardian_first_name.ilike(search_term),
                    Player.guardian_last_name.ilike(search_term)
                )
            )

        # Get sorted players
        players = query.order_by(Player.last_name, Player.first_name).all()

        # Create CSV string
        si = StringIO()
        writer = csv.writer(si)
        
        # Write comprehensive headers with all available information
        writer.writerow([
            # Basic Player Information
            'Season', 'First Name', 'Last Name', 'Birth Year', 'Team', 'Position',
            
            # Jersey and Equipment
            'Jersey Number', 'Jersey Size', 'Socks Size', 'Jacket Size', 'USA Hockey Number',
            
            # Father/Dad Information
            'Dad First Name', 'Dad Last Name', 'Dad Phone', 'Dad Email',
            
            # Mother/Mom Information
            'Mom First Name', 'Mom Last Name', 'Mom Phone', 'Mom Email',
            
            # Address Information
            'Address', 'City', 'State', 'Zip Code',
            
            # Financial Information
            'Paid Tuition', 'Total Tuition Amount', 'Amount Paid',
            
            # Documentation and Legal
            'Signed Waiver', 'Birth Certificate',
            
            # Legacy Fields (for backward compatibility)
            'Date of Birth', 'Guardian First Name', 'Guardian Last Name', 'Paid Status',
            
            # System Information
            'Created Date', 'Last Updated'
        ])
        
        # Write comprehensive player data
        for player in players:
            writer.writerow([
                # Basic Player Information
                player.season or '',
                player.first_name or '',
                player.last_name or '',
                player.birth_year or '',
                player.team or '',
                player.position or '',
                
                # Jersey and Equipment
                player.jersey_number or '',
                player.jersey_size or '',
                player.socks or '',
                player.jacket or '',
                player.usa_hockey_number or '',
                
                # Father/Dad Information
                player.dad_first_name or '',
                player.dad_last_name or '',
                player.dad_phone or '',
                player.dad_email or '',
                
                # Mother/Mom Information
                player.mom_first_name or '',
                player.mom_last_name or '',
                player.mom_phone or '',
                player.mom_email or '',
                
                # Address Information
                player.address or '',
                player.city or '',
                player.state or '',
                player.zip_code or '',
                
                # Financial Information
                'Yes' if player.paid_tuition else 'No',
                f"${player.total_tuition_amount:.2f}" if player.total_tuition_amount else '',
                f"${player.amount_paid:.2f}" if player.amount_paid else '',
                
                # Documentation and Legal
                'Yes' if player.signed_waiver else 'No',
                'Yes' if player.birth_certificate else 'No',
                
                # Legacy Fields
                player.date_of_birth.strftime('%m/%d/%Y') if player.date_of_birth else '',
                player.guardian_first_name or '',
                player.guardian_last_name or '',
                'Yes' if player.paid else 'No',
                
                # System Information
                player.created_at.strftime('%m/%d/%Y %H:%M') if player.created_at else '',
                player.updated_at.strftime('%m/%d/%Y %H:%M') if player.updated_at else ''
            ])

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=roster_export.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    except Exception as e:
        print(f"Error exporting roster: {str(e)}")
        flash('Error exporting roster. Please try again.', 'danger')
        return redirect(url_for('main.roster'))

@main.route("/player/add", methods=["GET", "POST"])
@login_required
def add_player():
    """Add a new player with comprehensive information."""
    form = PlayerForm()
    if form.validate_on_submit():
        try:
            # Create player with all new fields
            player = Player(
                # Basic Information
                season=form.season.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                birth_year=form.birth_year.data,
                team=form.team.data,
                position=form.position.data,
                
                # Jersey and Equipment
                jersey_number=form.jersey_number.data,
                jersey_size=form.jersey_size.data,
                socks=form.socks.data,
                jacket=form.jacket.data,
                usa_hockey_number=form.usa_hockey_number.data,
                
                # Father Information
                dad_first_name=form.dad_first_name.data,
                dad_last_name=form.dad_last_name.data,
                dad_phone=form.dad_phone.data,
                dad_email=form.dad_email.data,
                
                # Mother Information
                mom_first_name=form.mom_first_name.data,
                mom_last_name=form.mom_last_name.data,
                mom_phone=form.mom_phone.data,
                mom_email=form.mom_email.data,
                
                # Address Information
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                zip_code=form.zip_code.data,
                
                # Financial Information
                paid_tuition=form.paid_tuition.data,
                total_tuition_amount=form.total_tuition_amount.data or 0.0,
                amount_paid=form.amount_paid.data or 0.0,
                
                # Documentation and Legal
                signed_waiver=form.signed_waiver.data,
                birth_certificate=form.birth_certificate.data,
                
                # Legacy fields for backward compatibility
                date_of_birth=form.date_of_birth.data,
                guardian_first_name=form.guardian_first_name.data,
                guardian_last_name=form.guardian_last_name.data,
                paid=form.paid.data
            )
            
            db.session.add(player)
            db.session.flush()  # Get the player ID
            
            # Handle document upload
            if form.document_upload.data:
                document = save_document(
                    form.document_upload.data, 
                    player.id, 
                    'birth_certificate' if form.birth_certificate.data else 'general'
                )
                if document:
                    flash('Document uploaded successfully!', 'success')
                else:
                    flash('Document upload failed. Please try again.', 'warning')
            
            db.session.commit()
            flash('Player added successfully!', 'success')
            return redirect(url_for('main.roster'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error adding player. Please try again.', 'danger')
            print(f"Error adding player: {str(e)}")
            import traceback
            traceback.print_exc()
    
    return render_template("player_form.html", form=form, title="Add Player")

@main.route("/player/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_player(id):
    """Edit an existing player."""
    player = Player.query.get_or_404(id)
    form = PlayerForm(obj=player)
    
    if form.validate_on_submit():
        print(f"Form validated successfully for player {player.id}")
        try:
            # Update all comprehensive player fields
            # Basic Information
            player.season = form.season.data
            player.first_name = form.first_name.data
            player.last_name = form.last_name.data
            player.birth_year = form.birth_year.data
            player.team = form.team.data
            player.position = form.position.data
            
            # Jersey and Equipment
            player.jersey_number = form.jersey_number.data
            player.jersey_size = form.jersey_size.data
            player.socks = form.socks.data
            player.jacket = form.jacket.data
            player.usa_hockey_number = form.usa_hockey_number.data
            
            # Father Information
            player.dad_first_name = form.dad_first_name.data
            player.dad_last_name = form.dad_last_name.data
            player.dad_phone = form.dad_phone.data
            player.dad_email = form.dad_email.data
            
            # Mother Information
            player.mom_first_name = form.mom_first_name.data
            player.mom_last_name = form.mom_last_name.data
            player.mom_phone = form.mom_phone.data
            player.mom_email = form.mom_email.data
            
            # Address Information
            player.address = form.address.data
            player.city = form.city.data
            player.state = form.state.data
            player.zip_code = form.zip_code.data
            
            # Financial Information
            player.paid_tuition = form.paid_tuition.data
            player.total_tuition_amount = form.total_tuition_amount.data or 0.0
            player.amount_paid = form.amount_paid.data or 0.0
            
            # Documentation and Legal
            player.signed_waiver = form.signed_waiver.data
            player.birth_certificate = form.birth_certificate.data
            
            # Legacy fields (for backward compatibility)
            player.date_of_birth = form.date_of_birth.data
            player.guardian_first_name = form.guardian_first_name.data
            player.guardian_last_name = form.guardian_last_name.data
            player.paid = form.paid.data
            
            # Handle document upload if provided
            if form.document_upload.data:
                document_file = form.document_upload.data
                if allowed_file(document_file.filename):
                    try:
                        document = save_document(document_file, player.id, 'general')
                        if document:
                            # Document was saved successfully, it's already added to the session
                            # Reset file pointer
                            document_file.seek(0)
                        else:
                            flash('Error saving document. Please try again.', 'warning')
                    except Exception as e:
                        flash(f'Error saving document: {str(e)}', 'warning')
            
            player.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Player updated successfully!', 'success')
            return redirect(url_for('main.view_player', id=player.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating player: {str(e)}. Please try again.', 'danger')
            print(f"Error updating player: {str(e)}")
            print(f"Player ID: {player.id}")
            print(f"Form data: {form.data}")
            traceback.print_exc()
    
    if request.method == "POST" and not form.validate():
        print(f"Form validation failed for player {player.id}")
        print(f"Form errors: {form.errors}")
        flash('Please correct the errors below.', 'danger')
    
    return render_template("player_form.html", form=form, title="Edit Player", player=player)

@main.route("/player/<int:id>/delete", methods=["POST"])
@login_required
def delete_player(id):
    """Delete a player."""
    try:
        # Debug: Print form data
        print(f"DEBUG: Delete request form data: {dict(request.form)}")
        print(f"DEBUG: CSRF token from form: {request.form.get('csrf_token')}")
        
        player = Player.query.get_or_404(id)
        db.session.delete(player)
        db.session.commit()
        flash('Player deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting player. Please try again.', 'danger')
        print(f"Error deleting player: {str(e)}")
    
    return redirect(url_for('main.roster'))

@main.route("/api/player/<int:id>/delete", methods=["POST"])
@login_required
def api_delete_player(id):
    """API endpoint to delete a player - bypasses CSRF protection."""
    try:
        print(f"DEBUG: API Delete request form data: {dict(request.form)}")
        
        player = Player.query.get_or_404(id)
        db.session.delete(player)
        db.session.commit()
        flash('Player deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting player. Please try again.', 'danger')
        print(f"Error in API delete: {str(e)}")
    
    return redirect(url_for('main.roster'))

@main.route("/player/<int:id>")
@login_required
def view_player(id):
    """View a single player's details."""
    player = Player.query.get_or_404(id)
    return render_template("player_detail.html", player=player)

@main.route("/player/<int:player_id>/document/<int:document_id>/download")
@login_required
def download_document(player_id, document_id):
    """Securely download a player document."""
    try:
        # Verify the document belongs to the specified player
        document = PlayerDocument.query.filter_by(
            id=document_id, 
            player_id=player_id
        ).first_or_404()
        
        # Check if file exists
        if not os.path.exists(document.file_path):
            print(f"Document not found at path: {document.file_path}")
            flash('Document file not found on disk. Please contact an administrator.', 'error')
            return redirect(url_for('main.view_player', id=player_id))
        
        # Send the file
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.original_filename,
            mimetype=document.mime_type
        )
        
    except Exception as e:
        print(f"Error downloading document: {str(e)}")
        print(f"Document path: {document.file_path if 'document' in locals() else 'Unknown'}")
        flash(f'Error downloading document: {str(e)}', 'error')
        return redirect(url_for('main.view_player', id=player_id))

### Error Handlers ###
@main.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@main.route("/debug/routes")
def list_routes():
    """List all registered routes for debugging."""
    output = []
    for rule in current_app.url_map.iter_rules():
        output.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify(output)

@main.route("/debug/players")
@login_required
def debug_players():
    players = Player.query.all()
    debug_info = []
    for player in players:
        debug_info.append({
            'id': player.id,
            'name': f"{player.first_name} {player.last_name}",
            'team': repr(player.team),  # repr() will show exact string value including quotes
            'season': repr(player.season),
            'team_type': type(player.team).__name__,
            'season_type': type(player.season).__name__
        })
    return jsonify(debug_info)


### File Management Routes ###
@main.route("/files")
@main.route("/files/<int:folder_id>")
@login_required
def files(folder_id=None):
    """Display files and folders (shared across all users)."""
    try:
        # Get current folder if specified
        current_folder = None
        if folder_id:
            current_folder = Folder.query.filter_by(id=folder_id).first_or_404()
        
        # Get subfolders and files in current directory (shared across all users)
        folders = Folder.query.filter_by(
            parent_id=folder_id
        ).order_by(Folder.name).all()
        
        files = File.query.filter_by(
            folder_id=folder_id
        ).order_by(File.original_name).all()
        
        # Build breadcrumb navigation
        breadcrumbs = []
        if current_folder:
            folder = current_folder
            while folder:
                breadcrumbs.insert(0, folder)
                folder = folder.parent
        
        return render_template("files.html",
                             folders=folders,
                             files=files,
                             current_folder=current_folder,
                             breadcrumbs=breadcrumbs)
    except Exception as e:
        print(f"Error in files route: {str(e)}")
        flash('Error loading files. Please try again.', 'danger')
        return redirect(url_for('main.dashboard'))


@main.route("/test-upload", methods=["POST"])
def test_upload():
    """Test upload without authentication."""
    print("=== TEST UPLOAD ROUTE HIT ===")
    print(f"Files: {list(request.files.keys())}")
    print(f"Form: {dict(request.form)}")
    return jsonify({"status": "test upload received"})

@main.route("/files/browse")
@main.route("/files/browse/<int:folder_id>")
@login_required
def browse_files(folder_id=None):
    """Browse files and folders in a specific directory."""
    try:
        # Get folders in the current directory
        folders = Folder.query.filter_by(parent_id=folder_id).order_by(Folder.name).all()
        
        # Get files in the current directory
        files = File.query.filter_by(folder_id=folder_id).order_by(File.original_name).all()
        
        # Prepare folder data
        folder_list = []
        for folder in folders:
            folder_list.append({
                'id': folder.id,
                'name': folder.name,
                'description': folder.description,
                'color': folder.color
            })
        
        # Prepare file data
        file_list = []
        for file in files:
            file_list.append({
                'id': file.id,
                'original_name': file.original_name,
                'mime_type': file.mime_type,
                'file_size': file.file_size,
                'description': file.description
            })
        
        return jsonify({
            'success': True,
            'folders': folder_list,
            'files': file_list,
            'current_folder_id': folder_id
        })
        
    except Exception as e:
        print(f"File browse error: {str(e)}")
        return jsonify({'success': False, 'error': 'Browse failed'}), 500


@main.route("/files/search")
@login_required
def search_files():
    """Search files by name or description."""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'Search query required'})
        
        # Search in file names and descriptions
        files = File.query.filter(
            db.or_(
                File.original_name.ilike(f'%{query}%'),
                File.description.ilike(f'%{query}%')
            )
        ).limit(20).all()
        
        file_list = []
        for file in files:
            file_list.append({
                'id': file.id,
                'original_name': file.original_name,
                'mime_type': file.mime_type,
                'file_size': file.file_size,
                'description': file.description
            })
        
        return jsonify({
            'success': True,
            'files': file_list,
            'count': len(file_list)
        })
        
    except Exception as e:
        print(f"File search error: {str(e)}")
        return jsonify({'success': False, 'error': 'Search failed'}), 500


@main.route("/files/upload", methods=["POST"])
@login_required
def upload_file():
    """Handle file upload."""
    import os
    import uuid
    from werkzeug.utils import secure_filename
    
    try:
        print(f"=== UPLOAD DEBUG ===")
        print(f"User: {current_user.email if current_user and current_user.is_authenticated else 'Not authenticated'}")
        print(f"Files: {list(request.files.keys())}")
        print(f"Form: {dict(request.form)}")
        print(f"Folder ID from form: {request.form.get('folder_id')}")
        
        # Check authentication manually for debugging
        if not current_user or not current_user.is_authenticated:
            print("ERROR: User not authenticated!")
            return jsonify({'error': 'Authentication required'}), 401
        
        # Simple response first to test if route works
        if 'file' not in request.files:
            print("ERROR: No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        print(f"File received: {file.filename}")
        
        if file.filename == '':
            print("ERROR: Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        # Simplified - just save to a simple location for now
        original_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{original_name}"
        
        # Use the configured upload directory
        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_name)
        print(f"Saving to: {file_path}")
        
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        print(f"File saved successfully: {file_size} bytes")
        
        # Get folder_id from form data
        folder_id = request.form.get('folder_id')
        print(f"DEBUG: Raw folder_id from form: '{folder_id}' (type: {type(folder_id)})")
        
        # Handle various null/empty cases
        if folder_id and folder_id not in ['null', 'None', '']:
            try:
                folder_id = int(folder_id)
                print(f"DEBUG: Converted folder_id to: {folder_id}")
            except (ValueError, TypeError):
                print(f"DEBUG: Failed to convert folder_id '{folder_id}' to int, setting to None")
                folder_id = None
        else:
            print(f"DEBUG: folder_id is null/empty, setting to None")
            folder_id = None
        
        # Create database record
        db_file = File(
            name=unique_name,
            original_name=original_name,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type or 'application/octet-stream',
            folder_id=folder_id,
            user_id=current_user.id
        )
        
        db.session.add(db_file)
        db.session.commit()
        
        print("SUCCESS: Upload completed")
        
        return jsonify({
            'success': True,
            'file_id': db_file.id,
            'filename': db_file.original_name,
            'file': {
                'id': db_file.id,
                'name': db_file.original_name,
                'size': f"{file_size} bytes",
                'type': db_file.mime_type
            }
        })
        
    except Exception as e:
        print(f"EXCEPTION in upload: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@main.route("/files/create-folder", methods=["POST"])
@login_required
def create_folder():
    """Create a new folder."""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        if not data:
            print("No data received in create_folder request")
            return jsonify({'error': 'No data provided'}), 400
            
        # Debug CSRF token
        csrf_token = request.headers.get('X-CSRFToken')
        print(f"CSRF token from headers: {csrf_token}")
        print(f"Request headers: {dict(request.headers)}")
            
        name = data.get('name', '').strip()
        parent_id = data.get('parent_id')
        description = data.get('description', '').strip()
        color = data.get('color', 'primary')
        
        print(f"Create folder request: name={name}, parent_id={parent_id}, color={color}")
        
        if not name:
            return jsonify({'error': 'Folder name is required'}), 400
        
        # Validate parent folder exists if specified (no longer checking ownership)
        if parent_id:
            parent_folder = Folder.query.filter_by(id=parent_id).first()
            if not parent_folder:
                return jsonify({'error': 'Invalid parent folder'}), 400
        
        # Check for duplicate folder names in the same directory (shared across all users)
        existing = Folder.query.filter_by(
            name=name,
            parent_id=parent_id
        ).first()
        
        if existing:
            return jsonify({'error': 'A folder with this name already exists'}), 400
        
        # Create folder (shared, but keep user_id for tracking who created it)
        folder = Folder(
            name=name,
            description=description,
            color=color,
            parent_id=parent_id,
            user_id=current_user.id
        )
        
        db.session.add(folder)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'folder': {
                'id': folder.id,
                'name': folder.name,
                'color': folder.color,
                'file_count': 0
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating folder: {str(e)}")
        return jsonify({'error': 'Failed to create folder'}), 500


@main.route("/files/download/<int:file_id>")
@login_required
def download_file(file_id):
    """Download a file."""
    try:
        file = File.query.filter_by(id=file_id).first_or_404()
        
        # Check if file exists
        if not os.path.exists(file.file_path):
            print(f"File not found at path: {file.file_path}")
            flash('File not found on disk. Please contact an administrator.', 'error')
            return redirect(url_for('main.files'))
        
        # Update download count
        file.download_count += 1
        db.session.commit()
        
        return send_file(
            file.file_path,
            as_attachment=True,
            download_name=file.original_name,
            mimetype=file.mime_type
        )
        
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        print(f"File path: {file.file_path if 'file' in locals() else 'Unknown'}")
        flash('Error downloading file.', 'danger')
        return redirect(url_for('main.files'))


@main.route("/files/preview/<int:file_id>")
@login_required
def preview_file(file_id):
    """Preview a file in the browser (for supported formats)."""
    try:
        file = File.query.filter_by(id=file_id).first_or_404()
        
        # Check if file exists
        if not os.path.exists(file.file_path):
            print(f"File not found at path: {file.file_path}")
            flash('File not found on disk. Please contact an administrator.', 'error')
            return redirect(url_for('main.files'))
        
        # Check if file type is supported for preview
        if file.file_extension.lower() == 'pdf':
            # For PDFs, send file with inline disposition for browser preview
            return send_file(
                file.file_path,
                as_attachment=False,  # Don't download, display in browser
                mimetype='application/pdf'
            )
        elif file.is_image:
            # For images, send file inline
            return send_file(
                file.file_path,
                as_attachment=False,
                mimetype=file.mime_type
            )
        elif file.file_extension.lower() in ['txt', 'csv', 'json', 'xml', 'html', 'css', 'js']:
            # For text files, read and display content
            try:
                with open(file.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return render_template('file_preview.html', file=file, content=content)
            except UnicodeDecodeError:
                # If UTF-8 fails, try other encodings
                try:
                    with open(file.file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                    return render_template('file_preview.html', file=file, content=content)
                except:
                    flash('Unable to preview this file. Please download it instead.', 'warning')
                    return redirect(url_for('main.files'))
        else:
            flash('This file type cannot be previewed. Please download it instead.', 'info')
            return redirect(url_for('main.files'))
        
    except Exception as e:
        print(f"Error previewing file: {str(e)}")
        print(f"File path: {file.file_path if 'file' in locals() else 'Unknown'}")
        flash('Error previewing file.', 'danger')
        return redirect(url_for('main.files'))


@main.route("/files/delete/<int:file_id>", methods=["POST"])
@login_required
def delete_file(file_id):
    """Delete a file."""
    import os
    
    try:
        file = File.query.filter_by(id=file_id).first_or_404()
        
        # Delete physical file
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
        
        # Delete database record
        db.session.delete(file)
        db.session.commit()
        
        flash('File deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting file: {str(e)}")
        flash('Error deleting file.', 'danger')
    
    # Redirect back to the folder the file was in
    folder_id = request.form.get('folder_id')
    if folder_id and folder_id != 'None':
        return redirect(url_for('main.files', folder_id=folder_id))
    return redirect(url_for('main.files'))


@main.route("/files/delete-folder/<int:folder_id>", methods=["POST"])
@login_required
def delete_folder(folder_id):
    """Delete a folder and all its contents."""
    import os
    
    try:
        folder = Folder.query.filter_by(id=folder_id).first_or_404()
        parent_id = folder.parent_id
        
        # Recursively delete all files in this folder and subfolders
        def delete_folder_contents(f):
            # Delete files
            for file in f.files:
                if os.path.exists(file.file_path):
                    os.remove(file.file_path)
            
            # Recursively delete subfolders
            for subfolder in f.subfolders:
                delete_folder_contents(subfolder)
        
        delete_folder_contents(folder)
        
        # Delete the folder from database (cascade will handle files and subfolders)
        db.session.delete(folder)
        db.session.commit()
        
        flash('Folder deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting folder: {str(e)}")
        flash('Error deleting folder.', 'danger')
    
    # Redirect to parent folder or root
    if parent_id:
        return redirect(url_for('main.files', folder_id=parent_id))
    return redirect(url_for('main.files'))


### Bulk Import Routes ###
@main.route("/bulk-import", methods=["POST"])
@login_required
def bulk_import():
    """Handle bulk import of players from CSV."""
    from app.forms import BulkImportForm
    
    form = BulkImportForm()
    if not form.validate_on_submit():
        flash('Invalid form submission. Please try again.', 'danger')
        return redirect(url_for('main.roster'))
    
    try:
        file = form.csv_file.data
        
        # Read CSV content
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        imported_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start from row 2 (accounting for header)
            try:
                # Validate required fields
                if not row.get('first_name') or not row.get('last_name'):
                    errors.append(f"Row {row_num}: First name and last name are required")
                    error_count += 1
                    continue
                
                # Parse financial data
                total_tuition = 0.0
                amount_paid = 0.0
                try:
                    if row.get('total_tuition_amount'):
                        total_tuition = float(row['total_tuition_amount'])
                    if row.get('amount_paid'):
                        amount_paid = float(row['amount_paid'])
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid financial amount")
                    error_count += 1
                    continue
                
                # Create comprehensive player record
                player = Player(
                    # Basic Information
                    season=row.get('season', str(datetime.now().year)).strip(),
                    first_name=row['first_name'].strip(),
                    last_name=row['last_name'].strip(),
                    birth_year=row.get('birth_year', '').strip(),
                    team=row.get('team', '').strip(),
                    position=row.get('position', '').strip(),
                    
                    # Jersey and Equipment
                    jersey_number=row.get('jersey_number', '').strip(),
                    jersey_size=row.get('jersey_size', '').strip(),
                    socks=row.get('socks', '').strip(),
                    jacket=row.get('jacket', '').strip(),
                    usa_hockey_number=row.get('usa_hockey_number', '').strip(),
                    
                    # Father Information
                    dad_first_name=row.get('dad_first_name', '').strip(),
                    dad_last_name=row.get('dad_last_name', '').strip(),
                    dad_phone=row.get('dad_phone', '').strip(),
                    dad_email=row.get('dad_email', '').strip(),
                    
                    # Mother Information
                    mom_first_name=row.get('mom_first_name', '').strip(),
                    mom_last_name=row.get('mom_last_name', '').strip(),
                    mom_phone=row.get('mom_phone', '').strip(),
                    mom_email=row.get('mom_email', '').strip(),
                    
                    # Address Information
                    address=row.get('address', '').strip(),
                    city=row.get('city', '').strip(),
                    state=row.get('state', '').strip(),
                    zip_code=row.get('zip_code', '').strip(),
                    
                    # Financial Information
                    paid_tuition=row.get('paid_tuition', '').lower() in ['true', 'yes', '1'],
                    total_tuition_amount=total_tuition,
                    amount_paid=amount_paid,
                    
                    # Documentation and Legal
                    signed_waiver=row.get('signed_waiver', '').lower() in ['true', 'yes', '1'],
                    birth_certificate=row.get('birth_certificate', '').lower() in ['true', 'yes', '1'],
                    
                    # Legacy fields for backward compatibility
                    guardian_first_name=row.get('dad_first_name', '').strip(),
                    guardian_last_name=row.get('dad_last_name', '').strip(),
                    paid=row.get('paid_tuition', '').lower() in ['true', 'yes', '1']
                )
                
                db.session.add(player)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                error_count += 1
        
        # Commit all changes
        if imported_count > 0:
            db.session.commit()
            flash(f'Successfully imported {imported_count} players!', 'success')
        
        if error_count > 0:
            flash(f'{error_count} rows had errors. Check the details below.', 'warning')
            for error in errors[:10]:  # Show first 10 errors
                flash(error, 'danger')
        
        if imported_count == 0 and error_count == 0:
            flash('No data found in the CSV file.', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing CSV file: {str(e)}', 'danger')
    
    return redirect(url_for('main.roster'))


@main.route("/download-template")
@login_required
def download_template():
    """Download CSV template for bulk import."""
    try:
        # Create CSV template
        si = StringIO()
        writer = csv.writer(si)
        
        # Write headers for comprehensive player data
        writer.writerow([
            'season', 'first_name', 'last_name', 'birth_year', 'team', 'position',
            'jersey_number', 'jersey_size', 'socks', 'jacket', 'usa_hockey_number',
            'dad_first_name', 'dad_last_name', 'dad_phone', 'dad_email',
            'mom_first_name', 'mom_last_name', 'mom_phone', 'mom_email',
            'address', 'city', 'state', 'zip_code',
            'paid_tuition', 'total_tuition_amount', 'amount_paid',
            'signed_waiver', 'birth_certificate'
        ])
        
        # Write sample data
        writer.writerow([
            '2024', 'John', 'Doe', '2010', '8U', 'Forward',
            '15', 'S', 'M', 'S', '12345',
            'Mike', 'Doe', '555-1234', 'mike.doe@email.com',
            'Jane', 'Doe', '555-5678', 'jane.doe@email.com',
            '123 Main St', 'Bayonne', 'NJ', '07002',
            'true', '500.00', '500.00', 'true', 'true'
        ])
        writer.writerow([
            '2024', 'Sarah', 'Smith', '2011', '10U', 'Defense',
            '22', 'M', 'L', 'M', '67890',
            'Tom', 'Smith', '555-9876', 'tom.smith@email.com',
            'Lisa', 'Smith', '555-4321', 'lisa.smith@email.com',
            '456 Oak Ave', 'Jersey City', 'NJ', '07305',
            'false', '500.00', '250.00', 'true', 'false'
        ])
        
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=player_import_template.csv"
        output.headers["Content-type"] = "text/csv"
        return output
        
    except Exception as e:
        flash('Error generating template file.', 'danger')
        return redirect(url_for('main.roster'))


@main.route("/bulk-action", methods=["POST"])
@login_required
def bulk_action():
    """Handle bulk actions on selected players."""
    from flask_wtf.csrf import validate_csrf
    
    try:
        # Validate CSRF token manually
        validate_csrf(request.form.get('csrf_token'))
        
        action = request.form.get('action')
        player_ids = request.form.getlist('player_ids')
        
        if not player_ids:
            flash('No players selected.', 'warning')
            return redirect(url_for('main.roster'))
        
        player_ids = [int(id) for id in player_ids]
        players = Player.query.filter(Player.id.in_(player_ids)).all()
        
        if action == 'mark_paid':
            for player in players:
                player.paid_tuition = True
                player.paid = True  # Update legacy field too for compatibility
                player.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f'Marked {len(players)} players as paid.', 'success')
            
        elif action == 'mark_unpaid':
            for player in players:
                player.paid_tuition = False
                player.paid = False  # Update legacy field too for compatibility
                player.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f'Marked {len(players)} players as unpaid.', 'success')
            
        elif action == 'delete':
            count = len(players)
            for player in players:
                db.session.delete(player)
            db.session.commit()
            flash(f'Deleted {count} players.', 'success')
            
        else:
            flash('Invalid action.', 'danger')
            
    except Exception as e:
        db.session.rollback()
        if 'CSRF' in str(e):
            flash('CSRF token validation failed. Please try again.', 'danger')
        else:
            flash(f'Error performing bulk action: {str(e)}', 'danger')
    
    return redirect(url_for('main.roster'))

### Practice Plans Routes ###

@main.route("/practice-plans")
@login_required
def practice_plans():
    """Main practice plans landing page - list all teams."""
    teams = Team.query.order_by(Team.name).all()
    return render_template("practice_plans.html", teams=teams, title="Practice Plans")


@main.route("/practice-plans/team/<int:team_id>")
@login_required
def team_practice_plans(team_id):
    """View practice plans for a specific team."""
    team = Team.query.get_or_404(team_id)
    practice_plans = PracticePlan.query.filter_by(team_id=team_id).order_by(PracticePlan.date.desc()).all()
    return render_template("team_practice_plans.html", team=team, practice_plans=practice_plans, title=f"{team.name} Practice Plans")


@main.route("/practice-plans/team/add", methods=["GET", "POST"])
@login_required
def add_team():
    """Add a new team."""
    from app.practice_forms import TeamForm
    
    form = TeamForm()
    if form.validate_on_submit():
        try:
            team = Team(
                name=form.name.data,
                description=form.description.data,
                user_id=current_user.id
            )
            db.session.add(team)
            db.session.commit()
            flash('Team added successfully!', 'success')
            return redirect(url_for('main.practice_plans'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding team. Please try again.', 'danger')
            print(f"Error adding team: {str(e)}")
    
    return render_template("team_form.html", form=form, title="Add New Team")


@main.route("/practice-plans/team/<int:team_id>/edit", methods=["GET", "POST"])
@login_required
def edit_team(team_id):
    """Edit an existing team."""
    from app.practice_forms import TeamForm
    
    team = Team.query.get_or_404(team_id)
    form = TeamForm(obj=team)
    
    if form.validate_on_submit():
        try:
            team.name = form.name.data
            team.description = form.description.data
            db.session.commit()
            flash('Team updated successfully!', 'success')
            return redirect(url_for('main.practice_plans'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating team. Please try again.', 'danger')
            print(f"Error updating team: {str(e)}")
    
    return render_template("team_form.html", form=form, team=team, title="Edit Team")


@main.route("/practice-plans/team/<int:team_id>/delete", methods=["POST"])
@login_required
def delete_team(team_id):
    """Delete a team and all its practice plans."""
    team = Team.query.get_or_404(team_id)
    try:
        db.session.delete(team)
        db.session.commit()
        flash('Team deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting team. Please try again.', 'danger')
        print(f"Error deleting team: {str(e)}")
    
    return redirect(url_for('main.practice_plans'))


@main.route("/practice-plans/add/<int:team_id>", methods=["GET", "POST"])
@login_required
def add_practice_plan(team_id):
    """Add a new practice plan for a specific team."""
    from app.practice_forms import PracticePlanForm
    
    team = Team.query.get_or_404(team_id)
    form = PracticePlanForm()
    
    if form.validate_on_submit():
        try:
            # Parse external links (one per line)
            external_links = []
            if form.external_links.data:
                links = form.external_links.data.strip().split('\n')
                external_links = [link.strip() for link in links if link.strip()]
            
            practice_plan = PracticePlan(
                title=form.title.data,
                date=form.date.data,
                duration=form.duration.data,
                primary_focus=form.primary_focus.data,
                secondary_focus=form.secondary_focus.data,
                warm_up=form.warm_up.data,
                main_content=form.main_content.data,
                cool_down=form.cool_down.data,
                equipment_needed=form.equipment_needed.data,
                additional_notes=form.additional_notes.data,
                external_links=','.join(external_links) if external_links else None,
                team_id=team_id,
                user_id=current_user.id
            )
            
            db.session.add(practice_plan)
            db.session.flush()  # Get the ID without committing
            
            # Handle drill pieces
            for index, drill_form in enumerate(form.drill_pieces.data):
                if drill_form.get('drill_name') and drill_form.get('time'):  # Only add if has required fields
                    drill_piece = DrillPiece(
                        time=drill_form['time'],
                        drill_name=drill_form['drill_name'],
                        description=drill_form.get('description', ''),
                        link_attachment=drill_form.get('link_attachment', ''),
                        order_index=index,
                        practice_plan_id=practice_plan.id
                    )
                    db.session.add(drill_piece)
            
            # Handle file attachments
            if form.attachment_ids.data:
                attachment_ids = [int(id.strip()) for id in form.attachment_ids.data.split(',') if id.strip()]
                for file_id in attachment_ids:
                    # Check if file exists
                    file = File.query.get(file_id)
                    if file:
                        # Create attachment relationship
                        practice_plan.attachments.append(file)
            
            db.session.commit()
            flash('Practice plan added successfully!', 'success')
            return redirect(url_for('main.team_practice_plans', team_id=team_id))
        except Exception as e:
            db.session.rollback()
            flash('Error adding practice plan. Please try again.', 'danger')
            print(f"Error adding practice plan: {str(e)}")
    
    return render_template("practice_plan_form.html", form=form, team=team, title="Add Practice Plan")


@main.route("/practice-plans/<int:plan_id>/edit", methods=["GET", "POST"])
@login_required
def edit_practice_plan(plan_id):
    """Edit an existing practice plan."""
    from app.practice_forms import PracticePlanForm
    
    practice_plan = PracticePlan.query.get_or_404(plan_id)
    
    # Create form - use obj for GET, data for POST
    if request.method == 'GET':
        form = PracticePlanForm(obj=practice_plan)
    else:
        form = PracticePlanForm()
    
    if form.validate_on_submit():
        try:
            # Parse external links (one per line)
            external_links = []
            if form.external_links.data:
                links = form.external_links.data.strip().split('\n')
                external_links = [link.strip() for link in links if link.strip()]
            
            practice_plan.title = form.title.data
            practice_plan.date = form.date.data
            practice_plan.duration = form.duration.data
            practice_plan.primary_focus = form.primary_focus.data
            practice_plan.secondary_focus = form.secondary_focus.data
            practice_plan.warm_up = form.warm_up.data
            practice_plan.main_content = form.main_content.data
            practice_plan.cool_down = form.cool_down.data
            practice_plan.equipment_needed = form.equipment_needed.data
            practice_plan.additional_notes = form.additional_notes.data
            practice_plan.external_links = ','.join(external_links) if external_links else None
            
            # Handle drill pieces - clear existing and add new ones
            # Clear existing drill pieces
            DrillPiece.query.filter_by(practice_plan_id=practice_plan.id).delete()
            
            # Add new drill pieces
            for index, drill_form in enumerate(form.drill_pieces.data):
                if drill_form.get('drill_name') and drill_form.get('time'):  # Only add if has required fields
                    drill_piece = DrillPiece(
                        time=drill_form['time'],
                        drill_name=drill_form['drill_name'],
                        description=drill_form.get('description', ''),
                        link_attachment=drill_form.get('link_attachment', ''),
                        order_index=index,
                        practice_plan_id=practice_plan.id
                    )
                    db.session.add(drill_piece)
            
            # Handle file attachments
            if form.attachment_ids.data:
                attachment_ids = [int(id.strip()) for id in form.attachment_ids.data.split(',') if id.strip()]
                # Clear existing attachments
                practice_plan.attachments.clear()
                # Add new attachments
                for file_id in attachment_ids:
                    file = File.query.get(file_id)
                    if file:
                        practice_plan.attachments.append(file)
            else:
                # Clear all attachments if none selected
                practice_plan.attachments.clear()
            
            db.session.commit()
            print(f"DEBUG: Database committed successfully for plan {plan_id}")
            # Verify the data was saved
            updated_plan = PracticePlan.query.get(plan_id)
            print(f"DEBUG: After commit, plan has {len(updated_plan.drill_pieces)} drill pieces")
            for i, drill in enumerate(updated_plan.drill_pieces):
                print(f"DEBUG: Saved drill {i}: '{drill.drill_name}' - Description: '{drill.description}'")
            flash('Practice plan updated successfully!', 'success')
            return redirect(url_for('main.view_practice_plan', plan_id=practice_plan.id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating practice plan. Please try again.', 'danger')
            print(f"Error updating practice plan: {str(e)}")
    
    return render_template("practice_plan_form.html", form=form, practice_plan=practice_plan, team=practice_plan.team, title="Edit Practice Plan")


@main.route("/practice-plans/<int:plan_id>/delete", methods=["POST"])
@login_required
def delete_practice_plan(plan_id):
    """Delete a practice plan."""
    practice_plan = PracticePlan.query.get_or_404(plan_id)
    team_id = practice_plan.team_id
    
    try:
        db.session.delete(practice_plan)
        db.session.commit()
        flash('Practice plan deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting practice plan. Please try again.', 'danger')
        print(f"Error deleting practice plan: {str(e)}")
    
    return redirect(url_for('main.team_practice_plans', team_id=team_id))


@main.route("/practice-plans/<int:plan_id>/view")
@login_required
def view_practice_plan(plan_id):
    """View a practice plan in detail."""
    practice_plan = PracticePlan.query.get_or_404(plan_id)
    return render_template("practice_plan_detail.html", practice_plan=practice_plan, title=practice_plan.title)

@main.route("/practice-plans/<int:plan_id>/print")
@login_required
def print_practice_plan(plan_id):
    """Print view of a practice plan."""
    practice_plan = PracticePlan.query.get_or_404(plan_id)
    print(f"DEBUG: Rendering print template for plan {plan_id}")
    print(f"DEBUG: Template path: practice_plan_print.html")
    response = make_response(render_template('practice_plan_print.html', practice_plan=practice_plan, title=practice_plan.title))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@main.route("/practice-plans/<int:plan_id>/add-attachment", methods=["POST"])
@login_required
def add_practice_plan_attachment(plan_id):
    """Add file attachments to a practice plan."""
    practice_plan = PracticePlan.query.get_or_404(plan_id)
    
    # Handle both single file_id and multiple file_ids[]
    file_ids = request.form.getlist('file_ids[]')
    if not file_ids:
        # Fallback to single file_id for backward compatibility
        single_file_id = request.form.get('file_id')
        if single_file_id:
            file_ids = [single_file_id]
    
    if file_ids:
        try:
            added_count = 0
            for file_id in file_ids:
                file = File.query.get(file_id)
                if file and file not in practice_plan.attachments:
                    practice_plan.attachments.append(file)
                    added_count += 1
            
            if added_count > 0:
                db.session.commit()
                flash(f'{added_count} attachment(s) added successfully!', 'success')
            else:
                flash('No new attachments to add.', 'info')
        except Exception as e:
            db.session.rollback()
            flash('Error adding attachments. Please try again.', 'danger')
            print(f"Error adding attachments: {str(e)}")
    else:
        flash('No files selected.', 'warning')
    
    return redirect(url_for('main.view_practice_plan', plan_id=plan_id))


@main.route("/practice-plans/<int:plan_id>/remove-attachment/<int:file_id>", methods=["POST"])
@login_required
def remove_practice_plan_attachment(plan_id, file_id):
    """Remove a file attachment from a practice plan."""
    practice_plan = PracticePlan.query.get_or_404(plan_id)
    file = File.query.get(file_id)
    
    if file and file in practice_plan.attachments:
        try:
            practice_plan.attachments.remove(file)
            db.session.commit()
            flash('Attachment removed successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error removing attachment. Please try again.', 'danger')
            print(f"Error removing attachment: {str(e)}")
    
    return redirect(url_for('main.view_practice_plan', plan_id=plan_id))