"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static


from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from accounts.views import LoginView, RegisterView, home_page, guest_register_page
from django.views.generic import TemplateView
from addresses.views import checkout_address_create_view, checkout_address_reuse_view
from carts.views import cart_detail_api_view
from .views import contact_page
from billing.views import payment_method_view, payment_method_createview

urlpatterns = [

    url(r'^billing/payment-method/create/$', payment_method_createview, name='billing-payment-method-endpoint'),
    url(r'^billing/payment-method/$', payment_method_view, name='billing-payment-method'),
    url(r'^cart/', include('carts.urls', namespace='cart')),
	url(r'^product/', include('products.urls', namespace='product')),
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^register/guest', guest_register_page, name='guest'),
    url(r'^api/cart', cart_detail_api_view, name='api-cart'),
	url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^checkout/address/resuse/', checkout_address_reuse_view, name='reuse'),
    url(r'^checkout/address/create/', checkout_address_create_view, name='address'),
    url(r'^$', home_page, name='home'),
    url(r'^bootstrap/', TemplateView.as_view(template_name='bootstrap/example.html')),
    url(r'^register/', RegisterView.as_view(), name='register'),
    url(r'^contact/', contact_page, name='contact'),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
	urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

