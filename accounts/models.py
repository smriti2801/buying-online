from django.db import models
from django.contrib.auth.models import (
		AbstractBaseUser, BaseUserManager
		)
# from django.db.models.signals import pre_save

# Create your models here.

class UserManager(BaseUserManager):
	def create_user(self,email, full_name=None, password=None,is_active=True,is_staff=False,is_admin=False):
		if not email:
			raise ValueError("User must have an email address")
		if not password:
			raise ValueError("User must have a password")
		if not full_name:
			raise ValueError("User must have a fullname")

		user_obj=self.model(email=self.normalize_email(email),
							full_name=full_name)
		# can't include password in self.model bcoz 
		# we need to convert it to hashed-one and
		# then save
		user_obj.set_password(password)
		user_obj.staff=is_staff
		user_obj.admin=is_admin
		user_obj.active=is_active
		user_obj.save(using=self._db)
		return user_obj

	def create_staffuser(self,email,full_name, password=None):
		user = self.create_user(
				email,
				full_name,
				password=password,
				is_staff=True)
		return user

	def create_superuser(self,email,full_name,password=None):
		user = self.create_user(
				email,
				full_name,
				password=password,
				is_staff=True,
				is_admin=True)
		return user

class User(AbstractBaseUser):
	email=models.EmailField(unique=True, max_length=255)
	full_name=models.CharField(max_length=255,blank=True,null=True)
	active=models.BooleanField(default=True) # can login
	staff=models.BooleanField(default=False) # staff user non superuser
	admin=models.BooleanField(default=False) # superuser
	timestamp=models.DateTimeField(auto_now_add=True)

	objects=UserManager()

	USERNAME_FIELD='email' 
	#USERNAME_FIELD and password are required by default. 
	#so, i dont need to add them in my REQUIRED_FIELDS
	REQUIRED_FIELDS=['full_name']

	def __str__(self):
		return self.email

	def get_full_name(self):
		return self.email

	def get_short_name(self):
		return self.email

	def has_perm(self, perm, obj=None):
	# "Does the user have a specific permission?"
	# Simplest possible answer: Yes, always
		return True

	def has_module_perms(self, app_label):
	# "Does the user have permissions to view the app `app_label`?"
	# Simplest possible answer: Yes, always
		return True

	@property
	def is_staff(self):
		return self.staff

	@property
	def is_admin(self):
		return self.admin

	@property
	def is_admin(self):
		return self.admin

class GuestEmail(models.Model):
	email = models.EmailField()
	active = models.BooleanField(default=True)
	updated = models.DateTimeField(auto_now=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.email)



