from django.db import models
from carts.models import Cart
from billing.models import BillingProfile
from products.models import Product
from django.conf import settings
import math
# Create your models here.

from django.db.models.signals import pre_save, post_save
from ecommerce.utils import unique_order_id_generator
from addresses.models import Address
from django.core.urlresolvers import reverse

ORDER_STATUS_CHOICES = (
	('created', 'Created'),
	('paid', 'Paid'),
	('shipped', 'Shipped'),
	('refunded', 'Refunded'),
	)

class OrderManagerQuerySet(models.query.QuerySet):
	def by_request(self, request):
		billing_profile, created = BillingProfile.objects.new_or_get(request)
		return self.filter(billingprofile=billing_profile)


class OrderManager(models.Manager):
	def get_queryset(self):
		return OrderManagerQuerySet(self.model, using=self._db)

	def by_request(self, request):
		return self.get_queryset().by_request(request)

	def new_or_get(self, billingprofile, cart_obj):
		order_qs = Order.objects.filter(
				billingprofile=billingprofile, 
				cart=cart_obj, 
				active=True,
				status='created')

		#print(order_qs)

		if order_qs.count()==1:
			created = False
			order_obj =order_qs.first()
		else:
			order_obj, created = Order.objects.get_or_create(
				billingprofile=billingprofile, 
				cart=cart_obj)
			# created = True
		# print(order_obj)
		# print(created)
		# print(" --- created new order obj or not?")
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
	
	timestamp = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now =True)

	objects = OrderManager()

	class Meta:
		ordering =['-timestamp', '-updated']

	def get_absolute_url(self):
		return reverse('order:detail', kwargs={'order_id' : self.order_id})


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
		shipping_address_required = not self.cart.is_digital
		shipping_done = False
		if shipping_address_required and self.shipping_address:
			shipping_done = True
		elif shipping_address_required and not self.shipping_address:
			shipping_done = False
		else:
			shipping_done = True

		billing_profile = self.billingprofile
		#shipping_address = self.shipping_address
		billing_address = self.billing_address
		total = self.total
		if billing_profile and shipping_done and billing_address and total>0:
			return True
		return False

	def update_purchases(self):
		for p in self.cart.products.all():
			obj, created = ProductPurchase.objects.get_or_create(
					order_id=self.order_id,
					product = p,
					billing_profile = self.billingprofile,
				)
			obj.save()
		return ProductPurchase.objects.filter(order_id=self.order_id).count()

	def mark_paid(self):
		if self.status != 'paid':
			if self.check_done():
				self.status = "paid"
				self.save()
				self.update_purchases()
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


class ProductPurchaseManager(models.Manager):
	def all(self):
		return self.get_queryset().filter(refunded=False)

class ProductPurchase(models.Model):
	order_id = models.CharField(max_length=120)
	billing_profile = models.ForeignKey(BillingProfile)
	product = models.ForeignKey(Product)
	refunded = models.BooleanField(default=False)
	updated = models.DateTimeField(auto_now=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	objects = ProductPurchaseManager()

	def __str__(self):
		return self.product.title