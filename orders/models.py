from django.db import models
from carts.models import Cart
from billing.models import BillingProfile
import math
# Create your models here.

from django.db.models.signals import pre_save, post_save
from ecommerce.utils import unique_order_id_generator
from addresses.models import Address

ORDER_STATUS_CHOICES = (
	('created', 'Created'),
	('paid', 'Paid'),
	('shipped', 'Shipped'),
	('refunded', 'Refunded'),
	)

class OrderManager(models.Manager):
	def new_or_get(self, billingprofile, cart_obj):
		order_qs = Order.objects.filter(
				billingprofile=billingprofile, 
				cart=cart_obj, 
				active=True,
				status='created')

		print(order_qs)

		if order_qs.count()==1:
			created = False
			order_obj =order_qs.first()
		else:
			order_obj, created = Order.objects.get_or_create(
				billingprofile=billingprofile, 
				cart=cart_obj)
			# created = True
		print(order_obj)
		print(created)
		print(" --- created new order obj or not?")
		return order_obj, created

class Order(models.Model):
	billingprofile = models.ForeignKey(BillingProfile, null=True, blank=True)
	order_id = models.CharField(max_length=120, blank=True) # AB31DE3
	shipping_address = models.ForeignKey(Address, related_name="shipping_address", null=True, blank=True)
	billing_address = models.ForeignKey(Address, related_name="billing_address", null=True, blank=True)
	cart = models.ForeignKey(Cart)
	status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
	shipping_total = models.DecimalField(default=0, max_digits=100, decimal_places=2)
	total = models.DecimalField(default=0, max_digits=100, decimal_places=2)
	active = models.BooleanField(default=True)

	objects = OrderManager()

	def __str__(self):
		return str(self.order_id)

	# generate the order_id
	# generate the order total

	def update_total(self):
		# self == instance == Order
		cart_total = self.cart.total
		shipping_total = self.shipping_total
		total = math.fsum([cart_total,shipping_total])
		self.total = total
		self.save()
		return total


	def check_done(self):
		billing_profile = self.billingprofile
		shipping_address = self.shipping_address
		billing_address = self.billing_address
		total = self.total
		if billing_profile and shipping_address and billing_address and total>0:
			return True
		return False

	def mark_paid(self):
		if self.check_done():
			self.status = "paid"
			self.save()
		return self.status

def pre_save_create_order_id(sender, instance, *args, **kwargs):
	if not instance.order_id:
		instance.order_id=unique_order_id_generator(instance)
	qs = Order.objects.exclude(
			billingprofile=instance.billingprofile).filter(
			cart=instance.cart, 
			active=True)
	if qs.exists():
		qs.update(active=False)

pre_save.connect(pre_save_create_order_id, sender=Order)

def post_cart_save_receiver(sender, instance, created, *args, **kwargs):
	print(created)
	if not created: # if order not created
		cart_obj = instance
		id = cart_obj.id
		qs = Order.objects.filter(cart__id=id)
		print(qs)
					# instance.update_total() --- instance==cart_obj which 
			# doesn't have update_total(). we need to update total
			# for order. so it is qs.update_total(). no but, qs is
			# a queryset. i need to get the object so, i did this--
		if qs.count()==1:
			order_obj = qs.first()
			order_obj.update_total()

post_save.connect(post_cart_save_receiver, sender=Cart)

def post_order_save_receiver(sender, instance, created, *args, **kwargs):
	print(created) # if status is created ?
	if created:
		instance.update_total()

post_save.connect(post_order_save_receiver, sender=Order)