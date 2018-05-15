from django.shortcuts import render, redirect
from billing.models import BillingProfile
from .forms import AddressForm
from .models import Address

from django.utils.http import is_safe_url

def checkout_address_reuse_view(request):
	form = AddressForm(request.POST or None)
	context = {"form":form}
	next_ = request.GET.get('next')
	next_post = request.POST.get('next')
	redirect_path = next_ or next_post or None

	print(request.method +"resue method is this")
	
	if request.method=='POST':
		address_type = request.POST.get('address_type')
		print(address_type)
		request.session[address_type +"_address_id"]=request.POST.get('shipping_address')
		print(address_type +"_address_id")


		if is_safe_url(redirect_path,request.get_host()):
			return redirect(redirect_path)
		else:
			return redirect("cart:checkout")
	return redirect("cart:checkout")


def checkout_address_create_view(request):
	# instance is that of the form. and
	# we will attach the billing profile
	# and address type to it and save it
	# a modelform is saved it db via it's model

	# so, here i attached things to address model
	# in carts.views, i wil attach to order_obj

	form = AddressForm(request.POST or None)
	context = {"form":form}
	next_ = request.GET.get('next')
	next_post = request.POST.get('next')
	redirect_path = next_ or next_post or None
	
	if form.is_valid():
		instance=form.save(commit=False)
		billing_profile, created = BillingProfile.objects.new_or_get(request)
		if billing_profile is not None:
			instance.billing_profile =billing_profile
			instance.address_type = request.POST.get('address_type')
			instance.save()

			request.session[instance.address_type +"_address_id"]=instance.id
			print(instance.address_type +"_address_id")
		else:
			print("Error here")
			return redirect("cart:checkout")

		if is_safe_url(redirect_path,request.get_host()):
			return redirect(redirect_path)
		else:
			return redirect("cart:checkout")
		return redirect("cart:checkout")
