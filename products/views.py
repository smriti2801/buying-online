from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Product
from carts.models import Cart
from analytics.mixins import ObjectViewedMixin
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


class UserProducHistoryView(LoginRequiredMixin, ListView):
	template_name = "products/user-history.html"

	def get_context_data(self, *args, **kwargs):
		context = super(UserProducHistoryView, self).get_context_data(*args, **kwargs)
		request = self.request
		cart, new = Cart.objects.new_or_get(request)
		context['cart'] = cart
		return context

	def get_queryset(self, *args, **kwargs):
		request = self.request
		views = request.user.objectviewed_set.by_model(Product)
		print(views)
		#viewed_ids = [x.object_id for x in views]
		#return Product.objects.filter(pk__in=viewed_ids)
		return views


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



