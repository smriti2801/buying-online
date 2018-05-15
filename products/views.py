from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Product
from carts.models import Cart
from analytics.mixins import ObjectViewedMixin
# Create your views here.

class ProductListView(ListView):
	queryset = Product.objects.all()

	def get_context_data(self, *args, **kwargs):
		context = super(ProductListView, self).get_context_data(*args, **kwargs)
		request = self.request
		cart, new = Cart.objects.new_or_get(request)
		context['cart'] = cart
		return context

class ProductDetailView(ObjectViewedMixin, DetailView):
	queryset =Product.objects.all()

	def get_context_data(self, *args, **kwargs):
		context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
		request = self.request
		cart, new = Cart.objects.new_or_get(request)
		context['cart'] = cart
		return context



