Followed this to get started: https://docs.djangoproject.com/en/2.2/intro/tutorial01/
Not all of these need to be run; some of this is pick-and-choose. Just intended as a quick reference.

- Initialize a new Django project: `$ django-admin startproject mysite` (from the directory where all project files should go)
  
- Initialize an app within the project: `$ python manage.py startapp <app_name>`
  
- Add the app to `INSTALLED_APPS`:

  ```
  # <site_name>/settings.py
  INSTALLED_APPS = [
    '<app_name>.apps.<AppName>Config', # add this line
    'django.contrib.admin', # default stuff, etc.
    ...
    ]
  ```

- Start the server:

  `$ python manage.py runserver` or `$ python manage.py runserver 0.0.0.0:8000` to make available to other machines
  
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
  # <site_name>/urls.py
  from django.contrib import admin
  from django.urls import include, path

  urlpatterns = [
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
  ]
  ```
    
- Configure DB variables as desired in <site_name>/settings.py (engine, name)

- Set time zone while in <site_name>/settings.py

- Define DB models in <app_name>/models.py

- Use `makemigrations` to update the SQL code used to build DB schema: `$ python manage.py makemigrations <appname>`<br/>
To give the migration file a custom name, use `$ python manage.py makemigrations <appname> --name <custom_migration_name>`

- Initialize DB schema: `$ python manage.py migrate` (these steps also allow updating models)

- Show migrations: `$ python manage.py showmigrations`

- Revert to a previous migration: `$ python manage.py migrate <app_name> <migration_name>`<br/>
(for example, `$ python manage.py migrate metrics 0001_initial`)<br/>
It should be noted, however, that the migration still exists and will be applied when `migrate` command is next run.

- Create an admin user: `python managy.py createsuperuser` (then enter new creds)

- 



