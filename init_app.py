from lab4.init_db import init_db as init_lab4_db

def init_all():
    print("Initializing lab4 database...")
    init_lab4_db()
    print("All databases initialized successfully!")

if __name__ == '__main__':
    init_all() 