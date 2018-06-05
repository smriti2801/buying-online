from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils.http import is_safe_url
from .models import BillingProfile, Card

# Create your views here.

import stripe
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY")
STRIPE_PUB_KEY    = getattr(settings, "STRIPE_PUB_KEY")

stripe.api_key = STRIPE_SECRET_KEY

def payment_method_view(request):
	next_url=None
	next_=request.GET.get('next')
	if is_safe_url(next_,request.get_host()):
		next_url=next_

	print(next_url)

	context={
				"publish_key":STRIPE_PUB_KEY,
				"next_url":next_url
			}
	return render(request, 'billing/payment-method.html', context)


def payment_method_createview(request):
	if request.method=='POST' and request.is_ajax():

		billing_profile, created=BillingProfile.objects.new_or_get(request)
		print(billing_profile)
		if not billing_profile:
			return HttpResponse({"message":"Can't find the user"})

		token=request.POST.get("token")
		if token is not None:
			customer=stripe.Customer.retrieve(billing_profile.customer_id)
			card_response=customer.sources.create(source=token)

			card_obj=Card.objects.add_new(billing_profile,card_response)
			print(card_obj)
			
		return JsonResponse({"message":"Success! Payment method added"})
	return HttpResponse("error",status_code=401)
