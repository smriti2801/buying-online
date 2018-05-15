from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q

from products.models import Product

# Create your views here.

class SearchProductView(ListView):
	template_name = "search/views.html"
	queryset = Product.objects.all()

	def get_queryset(self, *args, **kwargs):
		query=self.request.GET.get('q')
		if query is not None:
			return Product.objects.search(query)
		return Product.objects.all()

	# def get_context_data(self, *args, **kwargs):
	# 	context = super(SearchProductView,self).get_context_data(*args, **kwargs)
	# 	print(context)
	# 	return context
		