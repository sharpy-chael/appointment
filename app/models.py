from . import db, bcrypt
from datetime import datetime

class Account(db.Model):
    __tablename__ = 'account'
    UserID = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    pass_word = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    
    user_profile = db.relationship('UserProfile', backref='account', uselist=False, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.pass_word = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.pass_word, password)

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    UserID = db.Column(db.Integer, db.ForeignKey('account.UserID'), primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    contact = db.Column(db.String(50))

class Status(db.Model):
    __tablename__ = 'status'
    Status_ID = db.Column(db.Integer, primary_key=True)
    Status_name = db.Column(db.String(50))
    
    appointments = db.relationship('Appointment', backref='status', lazy=True)

class Services(db.Model):
    __tablename__ = 'services'
    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    
    appointments = db.relationship('Appointment', backref='service', lazy=True)

class Appointment(db.Model):
    __tablename__ = 'appointment'
    appointmentID = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('account.UserID'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    Status_Id = db.Column(db.Integer, db.ForeignKey('status.Status_ID'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)