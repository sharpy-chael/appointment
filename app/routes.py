from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .decorators import login_required, role_required
from .models import Account, UserProfile, Appointment, Services, Status, db
from .auth import login_user

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("home.html")

@bp.route("/dashboard")
@login_required
def dashboard():
    # Get the current user's account
    account = Account.query.get(session['user_id'])
    
    # Get all appointments for this user, ordered by date (most recent first)
    appointments = Appointment.query.filter_by(UserID=account.UserID).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    return render_template("dashboard.html", account=account, appointments=appointments)

# ============== ADMIN ROUTES ==============
@bp.route("/admin")
@login_required
@role_required("admin")
def admin_area():
    filter_status = request.args.get('status', 'all')
    
    # Get all appointments
    if filter_status == 'all':
        appointments = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    else:
        status_obj = Status.query.filter_by(Status_name=filter_status.capitalize()).first()
        if status_obj:
            appointments = Appointment.query.filter_by(Status_Id=status_obj.Status_ID).order_by(Appointment.date.desc()).all()
        else:
            appointments = []
    
    # Statistics
    total_appointments = Appointment.query.count()
    pending_status = Status.query.filter_by(Status_name='Pending').first()
    confirmed_status = Status.query.filter_by(Status_name='Confirmed').first()
    
    pending_count = Appointment.query.filter_by(Status_Id=pending_status.Status_ID).count() if pending_status else 0
    confirmed_count = Appointment.query.filter_by(Status_Id=confirmed_status.Status_ID).count() if confirmed_status else 0
    total_users = Account.query.filter_by(role='user').count()
    
    return render_template("admin/admin.html", 
                         appointments=appointments,
                         filter_status=filter_status,
                         total_appointments=total_appointments,
                         pending_count=pending_count,
                         confirmed_count=confirmed_count,
                         total_users=total_users)

@bp.route('/admin/appointment/confirm/<int:id>')
@login_required
@role_required("admin")
def admin_confirm_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    confirmed_status = Status.query.filter_by(Status_name='Confirmed').first()
    
    if confirmed_status:
        appointment.Status_Id = confirmed_status.Status_ID
        db.session.commit()
        flash('Appointment confirmed successfully', 'success')
    else:
        flash('Error confirming appointment', 'danger')
    
    return redirect(url_for('main.admin_area'))

@bp.route('/admin/appointment/complete/<int:id>')
@login_required
@role_required("admin")
def admin_complete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    completed_status = Status.query.filter_by(Status_name='Completed').first()
    
    if completed_status:
        appointment.Status_Id = completed_status.Status_ID
        db.session.commit()
        flash('Appointment marked as completed', 'success')
    else:
        flash('Error completing appointment', 'danger')
    
    return redirect(url_for('main.admin_area'))

@bp.route('/admin/appointment/cancel/<int:id>')
@login_required
@role_required("admin")
def admin_cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    cancelled_status = Status.query.filter_by(Status_name='Cancelled').first()
    
    if cancelled_status:
        appointment.Status_Id = cancelled_status.Status_ID
        db.session.commit()
        flash('Appointment cancelled', 'success')
    else:
        flash('Error cancelling appointment', 'danger')
    
    return redirect(url_for('main.admin_area'))

@bp.route('/admin/services')
@login_required
@role_required("admin")
def admin_services():
    services = Services.query.all()
    return render_template('admin/services.html', services=services)

@bp.route('/admin/users')
@login_required
@role_required("admin")
def admin_users():
    users = Account.query.filter_by(role='user').all()
    return render_template('admin/users.html', users=users)

# ============== USER ROUTES ==============
@bp.route('/services')
def services():
    services = Services.query.all()
    return render_template('services.html', services=services)

@bp.route('/my-appointments')
@login_required
def my_appointments():
    filter_status = request.args.get('status', 'all')
    user_id = session['user_id']
    
    # Get appointments based on filter
    if filter_status == 'all':
        appointments = Appointment.query.filter_by(UserID=user_id).order_by(Appointment.date.desc()).all()
    else:
        status_obj = Status.query.filter_by(Status_name=filter_status.capitalize()).first()
        if status_obj:
            appointments = Appointment.query.filter_by(UserID=user_id, Status_Id=status_obj.Status_ID).order_by(Appointment.date.desc()).all()
        else:
            appointments = []
    
    return render_template('my_appointments.html', appointments=appointments, filter_status=filter_status)

@bp.route('/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
        service_id = request.form['service_id']
        date = request.form['date']
        time = request.form['time']
        
        # Get pending status
        pending_status = Status.query.filter_by(Status_name='Pending').first()
        
        if not pending_status:
            flash('Error: Pending status not found in database', 'danger')
            return redirect(url_for('main.book_appointment'))
        
        # Create new appointment
        appointment = Appointment(
            service_id=service_id,
            UserID=session['user_id'],
            date=date,
            time=time,
            Status_Id=pending_status.Status_ID
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    # GET request
    services = Services.query.all()
    service_id = request.args.get('service')
    return render_template('book_appointment.html', services=services, selected_service=service_id)

@bp.route('/cancel-appointment/<int:id>', methods=['GET'])
@login_required
def cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    # Security check: make sure the appointment belongs to the current user
    if appointment.UserID != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Find the "Cancelled" status
    cancelled_status = Status.query.filter_by(Status_name='Cancelled').first()
    
    if cancelled_status:
        appointment.Status_Id = cancelled_status.Status_ID
        db.session.commit()
        flash('Appointment cancelled successfully', 'success')
    else:
        flash('Error cancelling appointment', 'danger')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/profile', methods=['GET', 'POST']) 
@login_required
def profile():
    user = Account.query.get(session['user_id'])
    if request.method == 'POST':
        user.user_profile.name = request.form['name']
        user.user_profile.address = request.form['address']
        user.user_profile.contact = request.form['contact']
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('main.profile'))
    return render_template('profile.html', user=user)

# ============== AUTH ROUTES ==============
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        address = request.form['address']
        contact = request.form['contact']

        # Prevent duplicate email
        if Account.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('main.register'))

        account = Account(email=email)
        account.set_password(password)

        profile = UserProfile(
            name=name,
            address=address,
            contact=contact
        )

        account.user_profile = profile

        db.session.add(account)
        db.session.commit()

        flash('Account created successfully. Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Account.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('main.login'))

        # Save user session
        login_user(user.UserID, user.email, user.role)

        flash('Logged in successfully', 'success')

        # Role-based redirect
        if user.role == 'admin':
            return redirect(url_for('main.admin_area'))
        else:
            return redirect(url_for('main.dashboard'))

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('main.index'))