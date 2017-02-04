from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^set_user_default_state/$', user_default_order_state),
    url(r'^input_order/$', user_input_order),
    url(r'^check_order/$', check_order),
    url(r'^temp_to_order/$', temp_to_order),
    url(r'^modify_user/$', modify_user),
    url(r'^check_daily_quantity/$', check_daily_quantity),
    url(r'^check_monthly_quantity/$', check_monthly_quantity),
    url(r'^pressing_input/$', pressing_input),
    url(r'^$', ordering_system_root),
]