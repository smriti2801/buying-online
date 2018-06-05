from django.shortcuts import render, redirect
from django.conf import settings
from .models import Cart
from orders.models import Order
from products.models import Product
from accounts.forms import LoginForm, GuestForm
from addresses.forms import AddressForm
from addresses.models import Address
from billing.models import BillingProfile
from django.http import JsonResponse
# Create your views here.

import stripe
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY")
STRIPE_PUB_KEY    = getattr(settings, "STRIPE_PUB_KEY")
stripe.api_key = STRIPE_SECRET_KEY

def cart_detail_api_view(request):
	cart_obj, new_obj=Cart.objects.new_or_get(request=request)
	products = [{'id' : x.id,
				'url' : x.get_absolute_url(),
				'name' : x.title, 
				'price': x.price
				} for x in cart_obj.products.all()]

	cart_data = {
			"products":products, 
			"subtotal":cart_obj.subtotal, 
			"total":cart_obj.total
			}
	return JsonResponse(cart_data)

def cart_home(request):
	cart_obj, new_obj=Cart.objects.new_or_get(request=request)

	print(cart_obj.is_digital)

	context = {'cart' : cart_obj}
	return render(request, "carts/home.html", context)


def cart_update(request):
	product_id = request.POST.get('product_id')

	prod_obj=Product.objects.get(id=product_id)
	
	cart_obj, new_obj=Cart.objects.new_or_get(request)
	if prod_obj in cart_obj.products.all():
		cart_obj.products.remove(prod_obj)
		added=False
	else:
		cart_obj.products.add(prod_obj)
		added=True
	request.session['cart_items']=cart_obj.products.count()

	if request.is_ajax():
		# AJAX = Asynchronous Js And XML 
		print("Ajax request")
		json_data = {
			"added": added,
			"removed": not added,
			"cartItemCount": cart_obj.products.count()
		}
		return JsonResponse(json_data)
	return redirect("cart:home")
	# return redirect(prod_obj.get_absolute_url())

def cart_checkout(request):
	cart_obj, new_obj=Cart.objects.new_or_get(request)

	order_obj = None

	if new_obj or cart_obj.products.all==None:
		return redirect("cart:home")
	# else:
	# 	order_obj, new_obj =Order.objects.get_or_create(cart=cart_obj)
	address_form = AddressForm()
	login_form = LoginForm(request=request)
	guest_form = GuestForm(request=request)
	address_qs = None
	billing_address_id = request.session.get('billing_address_id', None)
	shipping_address_id = request.session.get('shipping_address_id', None)

	shipping_address_required = not cart_obj.is_digital

	has_card = False

	# if user or if a guest create a billingprofile
	billingprofile, billingprofile_created = BillingProfile.objects.new_or_get(request)
	print(billingprofile)

	# create an order based on the billing profile
	if billingprofile is not None:
		if request.user.is_authenticated():
			address_qs = Address.objects.filter(billing_profile=billingprofile) # only show these prev address when user is logged in

		print(billingprofile)
		print("is the billing profile passed in")
		print(cart_obj)

		order_obj, order_obj_created = Order.objects.new_or_get(billingprofile,cart_obj)
		if shipping_address_id:
			order_obj.shipping_address=Address.objects.get(id=shipping_address_id)
			del request.session['shipping_address_id']

		if billing_address_id:
			order_obj.billing_address=Address.objects.get(id=billing_address_id)
			del request.session['billing_address_id']

		if billing_address_id or shipping_address_id:
			order_obj.save()

		has_card = billingprofile.has_card

	print(request.method)

	if request.method == 'POST':
		"some check that order is done"
		is_prepared = order_obj.check_done()
		if is_prepared:
			did_charge,crg_msg=billingprofile.charge(order_obj)
		if did_charge:
			order_obj.mark_paid()
			request.session['cart_items']=0
			del request.session['cart_id']
			if not billingprofile.user:
				billingprofile.set_cards_inactive()
			return redirect('cart:success')
		else:
			print(crg_msg)
			return redirect("cart:checkout")

	context = {
				"object": order_obj, 
				"billing_profile": billingprofile,
				"login_form": login_form,
				"guest_form": guest_form,
				"address_form": address_form,
				"address_qs": address_qs,
				"has_card": has_card,
				"publish_key":STRIPE_PUB_KEY,				
				"shipping_address_required":shipping_address_required,

				}
	return render(request, "carts/checkout.html", context)


def cart_success_view(request):
	return render(request, "carts/success.html", {})
	