Followed this to get started: https://docs.djangoproject.com/en/2.2/intro/tutorial01/


- Initialize a new Django project:

  `$ django-admin startproject mysite` (from the directory where all project files should go)
  
- Initialize an app within the project:

  `$ python manage.py startapp polls`

- Start the server:

  `$ python manage.py runserver`
  
- Example of most simple view:

  ```
  # <app_name>/views.py
  from django.http import HttpResponse
  
  def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
  ```
  
 - Must add path to app's URLconf:
 
  ```
  # <app_name>/urls.py
  from django.urls import path
  from . import views

  urlpatterns = [
    path('', views.index, name='index'),
  ]
  ```

- Must add <app_name>.urls module to root URLconf:

  ```
  from django.contrib import admin
  from django.urls import include, path

  urlpatterns = [
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
  ]
  ```
    
- Configure DB variables as desired in <site_name>/settings.py (engine, name)

- Set time zone while in <site_name>/settings.py

- Initialize tables in DB:

  `$ python manage.py migrate`
  
- Define DB models in <app_name>/models.py
