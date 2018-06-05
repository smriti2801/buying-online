from django.db import models
import os
import random
from ecommerce.utils import unique_slug_generator
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.core.urlresolvers import reverse

# Create your models here.
def get_filename_ext(filepath):
	base_name=os.path.basename(filepath)
	name, ext= os.path.splitext(base_name)
	return name, ext

def upload_image_path(instance,filename):
	print(instance)
	print(filename)
	new_filename =random.randint(1,1234532)
	name, ext = get_filename_ext(filename)
	final_filename = '{new_filename}{ext}'.format(new_filename=new_filename,ext=ext)
	return "products/{new_filename}/{final_filename}".format(
			new_filename=new_filename,
			final_filename=final_filename
			)

class ProductQuerySet(models.query.QuerySet): 
	def search(self, query):
		lookups=(Q(title__icontains=query) | 
				Q(description__icontains=query) | 
				Q(price__icontains=query) |
				Q(tag__title__icontains=query))

		return self.filter(lookups).distinct()

	def featured(self):
		return self.filter(featured=True, active=True)

	def active(self):
		return self.filter(active=True)

class ProductModelManager(models.Manager):
	def get_queryset(self):
		return ProductQuerySet(self.model, using=self._db)

	def featured(self):
		return self.get_queryset().featured()

	def all(self):
		return self.get_queryset().active()

	def search(self, query):
		return self.get_queryset().search(query)

class Product(models.Model):
	title = models.CharField(max_length=120)
	description = models.TextField()
	slug = models.SlugField(blank=True, unique=True)
	price = models.DecimalField(decimal_places=2, max_digits=20, default=0.0)
	image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	active = models.BooleanField(default=True)
	featured = models.BooleanField(default=True)
	is_digital = models.BooleanField(default=False)

	objects = ProductModelManager()

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('product:detail', kwargs={'pk' : self.pk})

def rl_pre_save_receiver(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug=unique_slug_generator(instance)


pre_save.connect(rl_pre_save_receiver,sender=Product)


