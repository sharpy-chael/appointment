from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    bcrypt.init_app(app)

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()          
        init_default_data()     

    return app


def init_default_data():
    from .models import Status, Services
    from sqlalchemy import inspect

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    # STATUS TABLE
    if 'status' in tables:
        if not db.session.query(Status).first():
            db.session.add_all([
                Status(Status_name='Pending'),
                Status(Status_name='Confirmed'),
                Status(Status_name='Completed'),
                Status(Status_name='Cancelled')
            ])
            db.session.commit()

    # SERVICES TABLE
    if 'services' in tables:
        if not db.session.query(Services).first():
            db.session.add_all([
                Services(service_name='PC Checkup', description='Complete PC hardware and software checkup', price=500),
                Services(service_name='Virus Removal', description='Remove viruses and malware from your PC', price=300),
                Services(service_name='Data Recovery', description='Recover lost or deleted data', price=1000),
                Services(service_name='Hardware Upgrade', description='Upgrade PC components', price=800),
                Services(service_name='Software Installation', description='Install and configure software', price=200),
            ])
            db.session.commit()
