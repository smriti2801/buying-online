from django.conf.urls import url
from .views import cart_home, cart_update, cart_checkout, cart_success_view

urlpatterns = [
	url(r'^$', cart_home, name='home'),
	url(r'^success/$', cart_success_view, name='success'),
	url(r'^checkout/$', cart_checkout, name='checkout'),
	url(r'^update/$', cart_update, name='update'),
]