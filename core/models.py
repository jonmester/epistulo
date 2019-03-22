from django.db import models
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ckeditor.fields import RichTextField
from django.conf import settings

from django.core.files.storage import FileSystemStorage


class CustomUser(AbstractUser):
    is_creator = models.BooleanField(default=False)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #email = models.EmailField(max_length=254, blank=True)
    is_creator = models.BooleanField(default=False)
    
    creator_profile = models.ForeignKey('CreatorProfile', on_delete=models.SET_NULL, null=True)
    has_newsletter = models.BooleanField(default=False)
    subscriptions = models.ManyToManyField('Subscription', null=True, related_name='subscriptions')

class CreatorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='newsletter_profiles')
    name = models.CharField(max_length=100, unique=True)
    url_slug = models.SlugField(blank=True)
   
    description = models.TextField(max_length=1000, help_text="Write as much as you want about your newsletter and what readers will receive when subscribing")
   
    price = models.IntegerField(default=0)
    posts = models.ManyToManyField('CreatorPost')
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='subscriptions')
    stripe_product_id = models.CharField(max_length=1000, default=0)
    stripe_plan_id = models.CharField(max_length=1000, default=0)
    stripe_account_id = models.CharField(max_length=1000, blank=True)

    cover_pic = models.ImageField(upload_to = 'img_folder/', null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.url_slug = slugify(self.name)
        super(CreatorProfile, self).save(*args, **kwargs)

class CreatorPost(models.Model):
    PUBLICITY_CHOICES = (
        ('free', 'Free For All'),
        ('sneak', 'Sneak Peek'),
        ('exclusive', 'Exclusive')
        )

    title = models.CharField(max_length=100)
    content = RichTextField()
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    url_slug = models.SlugField(blank=True)
    publicity = models.CharField(max_length=20, choices=PUBLICITY_CHOICES, default='free')
    video = models.CharField(max_length=100, blank=True)
    featured_image = models.ImageField(upload_to = 'img_folder/', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.url_slug = slugify(self.title)
        super(CreatorPost, self).save(*args, **kwargs)
'''
class CreatorPostComment(models.Model):
    creator_post = models.ManyToManyField(CreatorPost)
    comment = models.TextField(max_length=1000)
    commentor = models.ManyToManyField(settings.AUTH_USER_MODEL)
    timestamp = models.DateTimeField(auto_now_add=True)
'''

class SubscriptionPlan(models.Model):
    plan_id = models.CharField(unique=True, max_length=1000)
    amount = models.IntegerField()
    nickname = models.CharField(unique=True, max_length=1000)
    product =  models.CharField(unique=True, max_length=1000)


# CUSTOMERS:
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=1000, primary_key=True)

    def __str__(self):
        return self.stripe_customer_id

# SUBSCRIPTIONS:
class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, default=None)
    newsletter = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, default=None)
    stripe_subscription_id = models.CharField(max_length=500, primary_key=True, default=None)
    stripe_customer_id = models.CharField(max_length=500, default=None)
    is_active = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    

    def __str__(self):
        return self.stripe_subscription_id


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=CreatorProfile)
def has_newsletter_activator(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.is_creator = True
        user.save()


@receiver(post_delete, sender=CreatorProfile)
def has_newsletter_deactivator(sender, instance, **kwargs):
    user = instance.user
    user.is_creator = False
    user.save()
