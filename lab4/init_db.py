from app import app, db, User, Role
from datetime import datetime, UTC

def init_db():
    with app.app_context():
        db.create_all()

        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
            db.session.commit()
            print('Admin role created successfully!')

        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            user_role = Role(name='user', description='Standard User')
            db.session.add(user_role)
            db.session.commit()
            print('User role created successfully!')

        admin = User.query.filter_by(login='admin').first()
        if not admin:
            admin = User(
                login='admin',
                first_name='Admin',
                last_name='User',
                role_id=admin_role.id,
                created_at=datetime.now(UTC)
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully!')
            print('Login: admin')
            print('Password: Admin123!')
        else:
            print('Admin user already exists!')
            admin.set_password('Admin123!')
            db.session.commit()
            print('Admin password has been reset!')
            print('Login: admin')
            print('Password: Admin123!')

if __name__ == '__main__':
    init_db() 