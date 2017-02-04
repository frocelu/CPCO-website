from django.conf.urls import url
from .views import list_Holidays, reset_default_weekends

urlpatterns = [
    url(r'^$', list_Holidays),
    url(r'^(?P<the_year>[0-9]+)$', list_Holidays, name='holidays'),
    url(r'^reset_default_weekends$', reset_default_weekends),
]