<<<<<<< HEAD
# BlackBox Movies — Complete Setup Guide

## Project Folder Structure

```
blackbox/                        ← root project folder
├── blackbox/                    ← Django project config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── movies/                      ← main app
│   ├── migrations/
│   ├── templates/
│   │   └── movies/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── card.html        ← reusable movie card
│   │       ├── detail.html
│   │       ├── watch.html
│   │       ├── genre.html
│   │       ├── search.html
│   │       ├── watchlist.html
│   │       ├── profile.html
│   │       ├── login.html
│   │       └── register.html
│   ├── __init__.py
│   ├── admin.py
│   ├── context_processors.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── static/
│   ├── css/
│   │   └── main.css
│   └── js/
│       └── main.js
├── media/                       ← auto-created for uploads
│   ├── posters/
│   ├── banners/
│   └── videos/
├── db.sqlite3                   ← auto-created
├── requirements.txt
└── manage.py
```

---

## Step 1: Install Python & Create Virtual Environment

```bash
# Make sure Python 3.10+ is installed
python --version

# Create your project folder
mkdir blackbox
cd blackbox

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

---

## Step 2: Install Django & Dependencies

```bash
pip install django pillow
```

Create `requirements.txt`:
```
django>=4.2
pillow>=10.0
```

---

## Step 3: Create Django Project & App

```bash
# Create the Django project
django-admin startproject blackbox .

# Create the movies app
python manage.py startapp movies
```

---

## Step 4: Create All Files

Copy all the files provided into their correct locations as shown in the structure above.

Key things to verify:
- `settings.py` has `'movies'` in INSTALLED_APPS
- `settings.py` has `'movies.context_processors.genres'` in TEMPLATES context_processors
- `blackbox/urls.py` includes `movies.urls`

---

## Step 5: Create Database & Superuser

```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Create admin superuser
python manage.py createsuperuser
# Enter username, email (optional), password
```

---

## Step 6: Run the Development Server

```bash
python manage.py runserver
```

Now open your browser:
- **Homepage:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

## Step 7: Upload Your First Movie (Admin Panel)

1. Go to http://127.0.0.1:8000/admin/
2. Log in with your superuser credentials
3. Click **Movies → Add Movie**
4. Fill in:
   - **Title** — movie name
   - **Description** — plot summary
   - **Genre** — pick from dropdown
   - **Release year** — e.g. 2024
   - **Rating** — e.g. 8.5
   - **Duration** — minutes (e.g. 120)
   - **Poster** — upload a JPG/PNG image (movie cover)
   - **Banner** — optional wide image for hero section
   - **Video file** — upload MP4 (or leave empty)
   - **Trailer URL** — YouTube embed URL like `https://www.youtube.com/embed/VIDEOID`
   - **Is featured** ✅ — shows in hero banner
   - **Is trending** ✅ — shows in trending row
5. Click **Save**

---

## Step 8: How to Get a YouTube Embed URL

1. Go to YouTube and find a movie trailer
2. Click **Share → Embed**
3. Copy only the `src` URL, e.g.:
   `https://www.youtube.com/embed/dQw4w9WgXcQ`
4. Paste that into the **Trailer URL** field

---

## Troubleshooting

### "No module named 'PIL'"
```bash
pip install pillow
```

### Images not showing
Make sure in `blackbox/urls.py` you have:
```python
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Static CSS not loading
```bash
python manage.py collectstatic
```

Or make sure `STATICFILES_DIRS` points to your static folder.

### Migration errors
```bash
python manage.py makemigrations movies
python manage.py migrate
```

---

## Features Summary

| Feature | How it works |
|---|---|
| Upload movies | Django admin panel |
| Browse by genre | /genre/action/, /genre/horror/, etc. |
| Search | /search/?q=title or live AJAX dropdown |
| Watch movies | /watch/movie-slug/ |
| Watchlist | Login required, AJAX toggle |
| User accounts | Register/Login/Logout |
| Reviews & ratings | Star rating system on detail page |
| Featured hero | Set is_featured=True in admin |
| Trending row | Set is_trending=True in admin |

---

## Optional: Free Deployment on Railway or Render

### Railway (free tier):
1. Go to railway.app
2. Connect your GitHub repo
3. Set environment variables:
   - `SECRET_KEY` = your secret key
   - `DEBUG` = False
4. Railway auto-detects Django and deploys

### Render (free tier):
1. Push code to GitHub
2. Go to render.com → New Web Service
3. Add `gunicorn blackbox.wsgi` as start command
4. Add `pip install -r requirements.txt` as build command


Author- Alex Augustine Gomes
=======
# BlackBoxMovies
A Django-based movie management system featuring a structured admin dashboard for adding, editing, and organizing movie records. Built with Python and Django, using Whitenoise for static file handling and Gunicorn for production deployment.
>>>>>>> 7be1a46c7e66080afe0ab9ceb4ffd3a8658c834e
