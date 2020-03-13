##Django-bookshop
This application is a simple project created as a project at school.

This is a store with used manuals where logged in users can buy or sell them

###The application includes:
* complete user profile support
* system which check if the given login or e-mail address is used by other user
* email address verification system

## Running the Project Locally

First, clone the repository to your local machine:
```bash
git clone https://github.com/izielin/bookshop.git
```
Create virtual environment
```bash
python -m venv venv
```

Install the requirements:
```bash
pip install -r requirements.txt
```

Apply the migrations:
```bash
python manage.py migrate
```

Finally, run the development server
```bash
python manage.py runserver
```

Create super user to get access to admin page
```bash
python manage.py createsuperuser
```

The project will be available at **127.0.0.1:8000**.

