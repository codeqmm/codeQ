# codeQ
Django Project

# 1. Make project dir and enter
mkdir school_site
cd school_site

# 2. Create virtual environment & activate
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows (PowerShell)
# .\venv\Scripts\Activate.ps1

# 3. Install Django and Pillow (for image uploads)
pip install django pillow

# 4. Start Django project
django-admin startproject config .

# 5. Create apps
python manage.py startapp core      # homepage, site pages
python manage.py startapp news      # news/posts
python manage.py startapp gallery   # photo gallery
python manage.py startapp people    # students, teachers, classes

# 6. Make initial migrations
python manage.py makemigrations
python manage.py migrate

# 7. Create admin user
python manage.py createsuperuser
