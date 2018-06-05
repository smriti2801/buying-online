from django.utils.text import slugify
import string
import random

def random_string_generator(size=10, char=string.ascii_lowercase+string.digits):
	return ''.join(random.choice(char) for _ in range(size))


def unique_key_generator(instance):
	size= random.randint(30, 45)
	key=random_string_generator(size)

	klass = instance.__class__
	qs_exists=klass.objects.filter(key=key).exists()
	if qs_exists:
		return unique_slug_generator(instance)
	return key


def unique_order_id_generator(instance):
	new_order_id=random_string_generator().upper()
	klass = instance.__class__
	qs=klass.objects.filter(order_id=new_order_id)
	if qs.exists():
		return unique_slug_generator(instance)
	return new_order_id

def unique_slug_generator(instance,new_slug=None):
	if new_slug is not None:
		slug=new_slug
	else:
		slug=slugify(instance.title)

	klass = instance.__class__

	if klass.objects.filter(slug=slug).exists():
		new_slug = "{slug}-{randstr}".format(
			slug=slug,
			randstr=random_string_generator(4))
		return unique_slug_generator(instance,new_slug)
	return slug