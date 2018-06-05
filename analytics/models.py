from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .signals import object_viewed_signal
from .utils import get_client_ip

User=settings.AUTH_USER_MODEL

class ObjectViewedQuerySet(models.query.QuerySet):
    def by_model(self, model_class):
        c_type = ContentType.objects.get_for_model(model_class)
        return self.filter(content_type=c_type)

class ObjectViewedManager(models.Manager):
    def get_queryset(self):
        return ObjectViewedQuerySet(self.model, using=self._db)

    def by_model(self, model_class):
        return self.get_queryset().by_model(model_class)

class ObjectViewed(models.Model):
    user            = models.ForeignKey(User, blank=True, null=True) # User instance instance.id
    ip_address      = models.CharField(max_length=120, blank=True, null=True) # IP field
    content_type    = models.ForeignKey(ContentType) # User, Product, Order, Cart, Address
    object_id       = models.PositiveIntegerField() # User id, Product id, Order id
    content_object  = GenericForeignKey('content_type', 'object_id') # Product instance
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = ObjectViewedManager()

    def __str__(self, ):
        return "%s viewed: %s" %(self.content_object, self.timestamp)

    class Meta:
        ordering = ['-timestamp'] # most recent saved show up first
        verbose_name = 'Object Viewed' 
        verbose_name_plural = 'Objects Viewed'



def object_viewed_receiver(sender, instance, request, *args, **kwargs):
    # print(sender)
    # print(instance)
    # print(request)
    # print(request.user)

    c_type = ContentType.objects.get_for_model(sender) # instance.__class__

    new_view_obj= ObjectViewed.objects.create(
                            user=request.user,
                            ip_address=get_client_ip,
                            content_type=c_type,
                            object_id=instance.id,
                            content_object=instance
                            )
object_viewed_signal.connect(object_viewed_receiver)