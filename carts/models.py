from django.db import models
from django.conf import settings

# Create your models here.
from products.models import Product
from django.db.models.signals import pre_save, m2m_changed

User = settings.AUTH_USER_MODEL


class CartModelManager(models.Manager):

	def new(self, user):
		user_obj=None
		if user is not None:
			if user.is_authenticated():
				user_obj=user
		return self.model.objects.create(user=user_obj)


	def new_or_get(self, request):
		cart_id=request.session.get("cart_id")
		qs = self.model.objects.filter(id=cart_id)
		if qs.count()==1:
			new_obj=False
			cart_obj=qs.first()
			if request.user.is_authenticated() and cart_obj.user is None:
				cart_obj.user=request.user
				cart_obj.save()	
		else:
			cart_obj=Cart.objects.new(user=request.user)
			new_obj=True
			request.session['cart_id']=cart_obj.id
		return cart_obj, new_obj


class Cart(models.Model):
	user = models.ForeignKey(User, null=True, blank=True)
	products = models.ManyToManyField(Product, blank=True)
	subtotal = models.DecimalField(default=0.00, decimal_places=2, max_digits=100)
	total = models.DecimalField(default=0.00, decimal_places=2, max_digits=100)
	updated = models.DateTimeField(auto_now=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	objects= CartModelManager()

	def __str__(self):
		return str(self.id)

	@property
	def is_digital(self):
		qs = self.products.all() #every product
		new_qs = qs.filter(is_digital=False)
		if new_qs.exists():
			return False
		return True



def m2m_save_cart_receiver(sender, instance, action, *args, **kwargs):
	if action=='post_add' or action=='post_remove' or action=='post_clear':
		print(action)
		products = instance.products.all()
		print(products)
		total=0
		for x in products:
			total+= x.price
		print(total)
		instance.subtotal=total
		instance.save()


m2m_changed.connect(m2m_save_cart_receiver,sender=Cart.products.through)

def pre_save_cart_receiver(sender, instance, *args, **kwargs):
	instance.total=instance.subtotal
	#instance.save()

pre_save.connect(pre_save_cart_receiver,sender=Cart)
