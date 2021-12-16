from django.db import models
import datetime
import stripe
from django.utils import timezone
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _

# Create your models here.

class CustomUser(AbstractUser):
    phone_No = models.CharField(max_length=10,blank=True,null=True)
    profile_pic = models.ImageField(null=True,blank=True,upload_to='profiles',default='avatar.jpg')
    is_member = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=40)
    Api_Key = models.CharField(max_length=256) 

class Membership(models.Model):
    
    class MembershipChoices(models.TextChoices):
        MEMBER = 'M', _('Member')
        NOT_MEMBER = 'N', _('Not_Member')

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=1,choices=MembershipChoices.choices)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    stripe_subscribe_id = models.CharField(max_length=40,blank=True,null=True)
    stripe_subscription_item_id = models.CharField(max_length=40,blank=True,null=True)

    def __str__(self):
        return self.user.username

class Inventory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null=True)
    image = models.ImageField(blank=False, upload_to='images')
    item_name = models.CharField(max_length=256,blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    filter_key = models.CharField(max_length=256,unique=True)

    def __str__(self):
        id=str(self.filter_key)
        return id

class PaymentMethodDatabase(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_method_id = models.CharField(max_length=256)
    amount = models.CharField(max_length=256)
    
    def __str__(self):
        return self.payment_method_id

class Payment(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()

    def __str__(self):
        return self.user.username

def post_save_user_receiver(sender, instance, created, *args, **kwargs):
    if created:
        import datetime

        membership = Membership.objects.get_or_create(
            user=instance,
            user_type='F',
            start_date=timezone.now(),
            end_date=timezone.now() + datetime.timedelta(days=14)
        )

post_save.connect(post_save_user_receiver, sender=settings.AUTH_USER_MODEL)