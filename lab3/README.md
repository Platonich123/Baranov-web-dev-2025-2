# Flask Web Application

A simple web application built with Flask that demonstrates user authentication, session management, and protected routes.

## Features

- Visit counter using Flask sessions
- User authentication with Flask-Login
- Remember me functionality
- Protected secret page
- Responsive Bootstrap UI
- Comprehensive test suite

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Set the Flask environment variables:
```bash
set FLASK_APP=app.py
set FLASK_ENV=development
```

2. Run the application:
```bash
flask run
```

The application will be available at http://localhost:5000

## Running Tests

To run the test suite:
```bash
pytest
```

## Default User Credentials

- Username: user
- Password: qwerty

## Project Structure

```
.
├── app.py              # Main application file
├── requirements.txt    # Project dependencies
├── tests/             # Test files
│   └── test_app.py    # Test suite
└── templates/         # HTML templates
    ├── base.html      # Base template
    ├── index.html     # Home page
    ├── login.html     # Login page
    └── secret.html    # Secret page
``` 