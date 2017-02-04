"""CPCO URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from user_management.views import login_ldap, user_logout


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^holidays/',include('holidays.urls')),
    url(r'^login/', login_ldap),
    url(r'^logout/', user_logout),
    url(r'^order/', include('ordering_system.urls')),
    # url(r'^load/', load_user_info),
    
] + staticfiles_urlpatterns()
