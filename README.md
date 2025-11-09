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


2) Project file structure (after following above)
school_site/
├─ config/
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ core/
│  ├─ views.py
│  └─ templates/core/
│      └─ home.html
├─ news/
│  ├─ models.py
│  ├─ admin.py
│  ├─ views.py
│  └─ templates/news/
│      ├─ news_list.html
│      └─ news_detail.html
├─ gallery/
│  ├─ models.py
│  ├─ admin.py
│  └─ templates/gallery/gallery.html
├─ people/
│  ├─ models.py
│  └─ admin.py
├─ templates/
│  └─ base.html
├─ static/
└─ manage.py

3) Edit config/settings.py

Open config/settings.py and:

Add apps to INSTALLED_APPS:

INSTALLED_APPS = [
    # default django apps...
    'django.contrib.staticfiles',
    'core',
    'news',
    'gallery',
    'people',
]


Add static & media settings (near end of file):

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # for collectstatic in production

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


TEMPLATES already exists; ensure 'DIRS': [os.path.join(BASE_DIR, 'templates')],

4) config/urls.py — wire everything up

Replace contents with:

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from core.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('news/', include('news.urls')),
    path('gallery/', include('gallery.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

5) core app — homepage

core/views.py:

from django.views.generic import TemplateView
from news.models import NewsPost
from gallery.models import GalleryImage

class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['latest_news'] = NewsPost.objects.published().order_by('-published_at')[:3]
        ctx['gallery_images'] = GalleryImage.objects.all()[:6]
        return ctx


core/templates/core/home.html (extends base; hero + news previews):

{% extends "base.html" %}
{% block content %}
<section class="py-5">
  <div class="container">
    <div class="row align-items-center">
      <div class="col-md-7">
        <h1 class="display-4">Welcome to {{ site_name|default:"Our School" }}</h1>
        <p class="lead">A premium learning environment — excellence in education.</p>
        <a href="{% url 'news:list' %}" class="btn btn-primary btn-lg">Latest News</a>
      </div>
      <div class="col-md-5">
        <img src="{% static 'img/school-hero.jpg' %}" class="img-fluid rounded" alt="School">
      </div>
    </div>

    <hr class="my-5">

    <h2>Latest News</h2>
    <div class="row">
      {% for post in latest_news %}
      <div class="col-md-4">
        <div class="card mb-4 shadow-sm">
          {% if post.featured_image %}
            <img src="{{ post.featured_image.url }}" class="card-img-top" alt="{{ post.title }}">
          {% endif %}
          <div class="card-body">
            <h5 class="card-title">{{ post.title }}</h5>
            <p class="card-text">{{ post.excerpt }}</p>
            <a href="{{ post.get_absolute_url }}" class="stretched-link">Read more</a>
          </div>
        </div>
      </div>
      {% empty %}
        <p>No news yet.</p>
      {% endfor %}
    </div>

    <h2 class="mt-5">Gallery</h2>
    <div class="row">
      {% for img in gallery_images %}
      <div class="col-md-2 mb-3">
        <img src="{{ img.image.url }}" class="img-fluid rounded" alt="{{ img.caption }}">
      </div>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}


(You'll need a hero image at static/img/school-hero.jpg — use any placeholder while developing.)

6) news app — models, admin, views, urls

news/models.py:

from django.db import models
from django.urls import reverse
from django.utils import timezone

class PublishedManager(models.Manager):
    def published(self):
        return self.filter(published_at__lte=timezone.now(), is_published=True)

class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='news/', blank=True, null=True)
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    published_objects = PublishedManager()

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:detail', args=[self.slug])


news/admin.py:

from django.contrib import admin
from .models import NewsPost

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'is_published')
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ('is_published',)
    search_fields = ('title', 'content')


news/views.py:

from django.views.generic import ListView, DetailView
from .models import NewsPost

class NewsListView(ListView):
    model = NewsPost
    template_name = 'news/news_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return NewsPost.published_objects.published()

class NewsDetailView(DetailView):
    model = NewsPost
    template_name = 'news/news_detail.html'
    slug_field = 'slug'


news/urls.py (create):

from django.urls import path
from .views import NewsListView, NewsDetailView

app_name = 'news'

urlpatterns = [
    path('', NewsListView.as_view(), name='list'),
    path('<slug:slug>/', NewsDetailView.as_view(), name='detail'),
]


news/templates/news/news_list.html:

{% extends "base.html" %}
{% block content %}
<div class="container py-5">
  <h1>News & Announcements</h1>
  <div class="row">
    {% for post in posts %}
      <div class="col-md-4">
        <div class="card mb-3">
          {% if post.featured_image %}
            <img src="{{ post.featured_image.url }}" class="card-img-top" alt="{{ post.title }}">
          {% endif %}
          <div class="card-body">
            <h5 class="card-title">{{ post.title }}</h5>
            <p class="card-text">{{ post.excerpt }}</p>
            <a href="{{ post.get_absolute_url }}">Read more</a>
          </div>
        </div>
      </div>
    {% empty %}
      <p>No news published yet.</p>
    {% endfor %}
  </div>
  {% if is_paginated %}
    <nav>
      <ul class="pagination">
        {% if page_obj.has_previous %}<li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}">Previous</a></li>{% endif %}
        <li class="page-item disabled"><span class="page-link">Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span></li>
        {% if page_obj.has_next %}<li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}">Next</a></li>{% endif %}
      </ul>
    </nav>
  {% endif %}
</div>
{% endblock %}


news/templates/news/news_detail.html:

{% extends "base.html" %}
{% block content %}
<div class="container py-5">
  <h1>{{ object.title }}</h1>
  <p class="text-muted">{{ object.published_at }}</p>
  {% if object.featured_image %}
    <img src="{{ object.featured_image.url }}" class="img-fluid mb-4" alt="{{ object.title }}">
  {% endif %}
  <div>
    {{ object.content|linebreaks }}
  </div>
</div>
{% endblock %}

7) gallery app — models, admin, urls, template

gallery/models.py:

from django.db import models

class GalleryImage(models.Model):
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption or f"Image {self.pk}"


gallery/admin.py:

from django.contrib import admin
from .models import GalleryImage

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'uploaded_at')


gallery/urls.py:

from django.urls import path
from .views import GalleryView

app_name = 'gallery'

urlpatterns = [
    path('', GalleryView.as_view(), name='gallery'),
]


gallery/views.py:

from django.views.generic import TemplateView
from .models import GalleryImage

class GalleryView(TemplateView):
    template_name = 'gallery/gallery.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['images'] = GalleryImage.objects.all().order_by('-uploaded_at')
        return ctx


gallery/templates/gallery/gallery.html:

{% extends "base.html" %}
{% block content %}
<div class="container py-5">
  <h1>Photo Gallery</h1>
  <div class="row">
    {% for img in images %}
    <div class="col-md-3 mb-3">
      <a href="{{ img.image.url }}" target="_blank">
        <img src="{{ img.image.url }}" class="img-fluid rounded shadow-sm" alt="{{ img.caption }}">
      </a>
    </div>
    {% empty %}
      <p>No images yet.</p>
    {% endfor %}
  </div>
</div>
{% endblock %}

8) people app — basic models and admin (for admin dashboard)

people/models.py:

from django.db import models

class SchoolClass(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    photo = models.ImageField(upload_to='students/', blank=True, null=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


people/admin.py:

from django.contrib import admin
from .models import SchoolClass, Teacher, Student

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'subject')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'school_class')

9) templates/base.html — premium look (Bootstrap 5 CDN + Google Fonts)

Create templates/base.html:

<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}Our School{% endblock %}</title>

    <!-- Google Font -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">

    <!-- Bootstrap 5 CSS (CDN) -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Your custom static CSS -->
    <link rel="stylesheet" href="{% static 'css/site.css' %}">
  </head>
  <body style="font-family: 'Inter', sans-serif;">
    <header class="bg-white shadow-sm">
      <nav class="navbar navbar-expand-lg navbar-light container">
        <a class="navbar-brand fw-bold" href="/">My Premium School</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarsExampleDefault">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarsExampleDefault">
          <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
            <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
            <li class="nav-item"><a class="nav-link" href="{% url 'news:list' %}">News</a></li>
            <li class="nav-item"><a class="nav-link" href="{% url 'gallery:gallery' %}">Gallery</a></li>
            <li class="nav-item"><a class="nav-link" href="/admin/">Admin</a></li>
          </ul>
        </div>
      </nav>
    </header>

    {% block content %}{% endblock %}

    <footer class="bg-dark text-white py-4 mt-5">
      <div class="container text-center">
        &copy; {{ now.year }} My Premium School — All rights reserved.
      </div>
    </footer>

    <!-- Bootstrap 5 JS (CDN) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>


Create static/css/site.css for small premium touches:

body { background: #f7f9fc; }
.navbar-brand { font-weight: 800; letter-spacing: .4px; }
.card { border-radius: 12px; }

10) Static & Media during development

Make sure STATICFILES_DIRS and MEDIA_ROOT set (we already added these). To serve media during development, config/urls.py included the static() helper under if DEBUG.

Place any static images in static/img/ (e.g., school-hero.jpg).

11) Run the project locally
# make migrations for new models
python manage.py makemigrations
python manage.py migrate

# create superuser if not done already
python manage.py createsuperuser

# run dev server
python manage.py runserver


Visit http://127.0.0.1:8000/ for the homepage, http://127.0.0.1:8000/admin/ to login to admin and add News posts, Gallery images, Students, Teachers, Classes.