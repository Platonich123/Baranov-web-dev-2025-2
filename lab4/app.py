from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, UTC
import re

app = Flask(__name__)
app.config.from_pyfile('config.py')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    users = db.relationship('User', backref='role', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(50))
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def validate_login(login):
    if not login:
        return False, "Login cannot be empty"
    if not re.match(r'^[a-zA-Z0-9]{5,}$', login):
        return False, "Login must contain only Latin letters and numbers, minimum 5 characters"
    return True, ""

def validate_password(password):
    if not password:
        return False, "Password cannot be empty"
    if len(password) < 8 or len(password) > 128:
        return False, "Password must be between 8 and 128 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if re.search(r'\s', password):
        return False, "Password must not contain spaces"
    if not re.match(r'^[a-zA-Zа-яА-Я0-9~!?@#$%^&*_\-+()\[\]{}><\/\\|"\',.:;]+$', password):
        return False, "Password contains invalid characters"
    return True, ""

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        user = User.query.filter_by(login=login).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid login or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<int:user_id>')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('view_user.html', user=user)

@app.route('/user/new', methods=['GET', 'POST'])
@login_required
def create_user():
    roles = Role.query.all()
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        middle_name = request.form.get('middle_name')
        role_id = request.form.get('role_id')

        login_valid, login_error = validate_login(login)
        password_valid, password_error = validate_password(password)

        if not login_valid or not password_valid:
            if not login_valid:
                flash(login_error)
            if not password_valid:
                flash(password_error)
            return render_template('user_form.html', 
                                login=login, 
                                first_name=first_name,
                                last_name=last_name,
                                middle_name=middle_name,
                                role_id=role_id,
                                roles=roles)

        try:
            user = User(
                login=login,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                role_id=role_id if role_id else None,
                created_at=datetime.now(UTC)
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('User successfully created')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating user')
            return render_template('user_form.html', 
                                login=login, 
                                first_name=first_name,
                                last_name=last_name,
                                middle_name=middle_name,
                                role_id=role_id,
                                roles=roles)

    return render_template('user_form.html', roles=roles, role_id=None)

@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        middle_name = request.form.get('middle_name')
        role_id = request.form.get('role_id')

        try:
            user.first_name = first_name
            user.last_name = last_name
            user.middle_name = middle_name
            user.role_id = role_id if role_id else None
            db.session.commit()
            flash('User successfully updated')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating user')
            return render_template('user_form.html', user=user, roles=roles)

    return render_template('user_form.html', user=user, roles=roles)

@app.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User successfully deleted')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user')
    return redirect(url_for('index'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(old_password):
            flash('Invalid current password')
            return render_template('change_password.html')

        password_valid, password_error = validate_password(new_password)
        if not password_valid:
            flash(password_error)
            return render_template('change_password.html')

        if new_password != confirm_password:
            flash('New passwords do not match')
            return render_template('change_password.html')

        try:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password successfully changed')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error changing password')
            return render_template('change_password.html')

    return render_template('change_password.html')

@app.route('/roles')
@login_required
def list_roles():
    roles = Role.query.all()
    return render_template('roles.html', roles=roles)

@app.route('/role/new', methods=['GET', 'POST'])
@login_required
def create_role():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if not name:
            flash('Role name cannot be empty')
            return render_template('role_form.html', name=name, description=description)
        try:
            role = Role(name=name, description=description)
            db.session.add(role)
            db.session.commit()
            flash('Role successfully created')
            return redirect(url_for('list_roles'))
        except Exception:
            db.session.rollback()
            flash('Error creating role')
            return render_template('role_form.html', name=name, description=description)
    return render_template('role_form.html')

@app.route('/role/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_role(role_id):
    role = Role.query.get_or_404(role_id)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if not name:
            flash('Role name cannot be empty')
            return render_template('role_form.html', role=role)
        try:
            role.name = name
            role.description = description
            db.session.commit()
            flash('Role successfully updated')
            return redirect(url_for('list_roles'))
        except Exception:
            db.session.rollback()
            flash('Error updating role')
            return render_template('role_form.html', role=role)
    return render_template('role_form.html', role=role)

@app.route('/role/<int:role_id>/delete', methods=['POST'])
@login_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    try:
        db.session.delete(role)
        db.session.commit()
        flash('Role successfully deleted')
    except Exception:
        db.session.rollback()
        flash('Error deleting role')
    return redirect(url_for('list_roles'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 