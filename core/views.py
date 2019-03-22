from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from datetime import date
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm, forms
from .forms import UserCreationForm, SignUpForm, CreatorProfileCreateForm, CreatorProfileEditForm, CreatorPostForm
from .models import CreatorProfile, Profile, CreatorPost, Subscription
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Profile
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import stripe
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.template.loader import render_to_string
from django.contrib import messages
from time import sleep
from django.http import JsonResponse, HttpResponseRedirect
import bleach
from django.contrib import messages
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .decorators import is_active
from django.contrib.auth import logout
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


# Push Notifications
from webpush import send_user_notification
import json


publishKey = settings.STRIPE_PUBLISHABLE_KEY
secretKey = settings.STRIPE_SECRET_KEY
stripe.api_key = secretKey


# 1. Utility functions
def get_profile(user):
    user_profile = Profile.objects.get(user=user)
    return user_profile

def get_newsletter(user):
    newsletter = CreatorProfile.objects.filter(user=user)
    return newsletter

def has_newsletter(user):
    newsletter = CreatorProfile.objects.filter(user=user)
    if newsletter.count() > 0:
        return True
    elif newsletter.count() == 0:
        return False


# 2. Basic views (home, discover & signup)

def home(request):
    if request.user.is_authenticated:
        subscriptions = Subscription.objects.filter(user=request.user)
        

        return render(request, 'home (copy).html', {
            'subscriptions': subscriptions,

        })
    else:
        return render(request, 'home (copy).html')

def discover_view(request):
    newsletter = CreatorProfile.objects.all()
    
    return render(request, 'discover.html', {
        'newsletter': newsletter,

        })


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            new_user = form.save()
            messages.info(request, "Thanks for registering", extra_tags='newbie')
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup (copy).html', {
        'form': form,

    })

def signup_redirect(request, slug):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, "Thanks for registering. You are now logged in.")
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)
            return redirect('newsletter_detail', slug=slug)

    else:
        form = SignUpForm()
    return render(request, 'registration/signup (copy).html', {
        'form': form
    })


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })

def logout_view(request):
    logout(request)

# 3. Views related to managing a newsletter

@login_required
def newsletter_create(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        user_profile = Profile.objects.get(user=request.user)
        form = CreatorProfileCreateForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()

            stripe.api_key = secretKey
            product = stripe.Product.create(
            name=instance.name,
            type='service',
            )

            instance.stripe_product_id = product.id

            plan = stripe.Plan.create(
                product=product.id,
                nickname='Subscription to {}'.format(instance.name),
                interval='month',
                currency='usd',
                amount=instance.price*100,
                )
            instance.stripe_plan_id = plan.id
            instance.save()
            request.user.is_creator = True
            messages.success(request, 'Success! You\'ve got your own newsletter now. Cool!')
            creator_profile = CreatorProfile.objects.get(user=request.user)
            return render(request, 'newsletter/newsletter_admin_new.html', {
            'creator_profile': creator_profile,
        })
            
    else:
        form = CreatorProfileCreateForm()
    return render(request, 'newsletter/create-new.html', {
        'form': form
    })

@login_required
def newsletter_edit_profile(request):
    creator_profile = CreatorProfile.objects.get(user=request.user)
    if request.method == 'POST':
        instance = CreatorProfile.objects.get(user=request.user)
        form = CreatorProfileEditForm(request.POST or None, request.FILES or None, instance=instance)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, 'You successfully edited your creator profile.')
            return redirect('go-to-profile')
        else:
            return HttpResponse("Sumtin fuckd up bro")
    else:
        instance = CreatorProfile.objects.get(user=request.user)
        form = CreatorProfileEditForm(request.POST or None, instance=instance)
        return render(request, 'newsletter/edit-profile-new.html', {
            'form': form,
            'creator_profile': creator_profile,
            
        })




@login_required
def newsletter_admin(request):
    if request.user.is_creator == True:
        creator_profile = CreatorProfile.objects.get(user=request.user)
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        creator_posts = creator_profile.posts.all().order_by('-timestamp')
        posts = creator_posts.order_by('-timestamp')
        subscribers = Subscription.objects.filter(newsletter=creator_profile).order_by('-timestamp')
        
        
        page = request.GET.get('page', 1)
        paginator = Paginator(creator_posts, 3)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        return render(request, 'newsletter/newsletter_admin_new.html', {
            'creator_profile': creator_profile,
            'posts': posts,
            'creator_posts': creator_posts,
            'subscribers': subscribers,
        
        })
    else:
        return redirect('create')


def newsletter_delete_profile(request):
    newsletter = CreatorProfile.objects.get(author=request.user)
    newsletter.delete()
    user_profile = get_profile(request.user)
    user_profile.has_newsletter = False
    user_profile.save()

    return redirect('home')


# 4. Views related to sending newsletter posts

# Utility function

def send_newsletters(instance, creator_profile):
    subscribers = Subscription.objects.filter(newsletter=creator_profile)
    subscriber_list = []
    for subscriber in subscribers:
            subscriber_list.append(subscriber.user.email)

    subject = instance.title
    from_email = '{}<jonmester3@gmail.com>'.format(creator_profile.name)
    to = subscriber_list
    html_message = instance.content
    plain_message = strip_tags(instance.content)
    context = {
    'title': subject,
    'content': html_message,
    'creator_profile': creator_profile,
    }

    html_body = render_to_string("email/index.html", context)


    email = EmailMultiAlternatives(subject, plain_message, from_email, to)
    email.attach_alternative(html_body, 'text/html')
    email.send()


def send_email_notifications(title, message, creator_id, video=None):
    creator_profile = CreatorProfile.objects.get(id=creator_id)
    subscribers = Subscription.objects.filter(newsletter=creator_profile)
    subscriber_list = []
    for subscriber in subscribers:
            subscriber_list.append(subscriber.user.email)
    subject = title
    from_email = '{}<email@gmail.com>'.format(creator_profile.name)
    to = subscriber_list
    html_message = message
    plain_message = strip_tags(message)
    context = {
    'title': subject,
    'content': html_message,
    'creator_profile': creator_profile,
    'video': video,
    }

    html_body = render_to_string("email/index.html", context)

    email = EmailMultiAlternatives(subject, plain_message, from_email, to)
    email.attach_alternative(html_body, 'text/html')
    email.send()


@login_required
def newsletter_write(request):
    creator_profile = CreatorProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = CreatorPostForm(request.POST or None, request.FILES or None)
        subscribers = creator_profile.subscribers.all()
        
        if form.is_valid():
            from django.core.mail import send_mail           
            instance = form.save(commit=False)
            video = request.POST.get('youtube-video-embed', '')
            if len(video) > 0:
                instance.video = video
                send_email_notifications(instance.title, instance.content, creator_profile.id, video)
            instance.save()
            creator_profile.posts.add(instance)
            
            creator_profile.save()
            

            

            
            post = CreatorPost.objects.get(title=instance.title)
            
            messages.success(request, 'Incredible! You published a new post. <a style="font-weight: bold;" href="/read/{}-{}"> Read it now. </a>'.format(post.url_slug, post.id))
            return redirect('newsletter_post_detail', slug=creator_profile.url_slug, post_slug=instance.url_slug)

    else:
        form = CreatorPostForm()
        return render(request, 'newsletter/create-post-new.html', {
            'form': form,
            'creator_profile': creator_profile,
        })

@login_required
def change_publicity_state(request, post_slug, post_id):
    try:
        post = CreatorPost.objects.get(url_slug=post_slug, id=post_id)
        if post.is_public == False:
            post.is_public = True
            post.save()
            messages.success(request, 'You made a post public.')
        else:
            post.is_public = False
            post.save()
            messages.success(request, 'You made a post exclusive.')
        return redirect('newsletter_admin')
    except:
        return redirect('home')



@login_required
def newsletter_delete_post(request, post_id):
    newsletter = CreatorProfile.objects.get(user=request.user)
    newsletter.posts.get(id=post_id).delete()
    newsletter.save()
    messages.success(request, 'You deleted a post.')
    return redirect('newsletter_detail', slug=newsletter.url_slug)


@login_required
def newsletter_edit(request, post_id):
    if request.method == 'POST':
        instance = CreatorPost.objects.get(id=post_id)
        creator_profile = CreatorProfile.objects.get(user=request.user)
        form = CreatorPostForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'You successfully edited a post')
            return redirect('newsletter_post_detail', slug=creator_profile.url_slug, post_slug=instance.url_slug)
    else:
        creator_profile = CreatorProfile.objects.get(user=request.user)
        instance = CreatorPost.objects.get(id=post_id)
        form = CreatorPostForm(request.POST or None, instance=instance)
        return render(request, 'newsletter/edit-post-new.html', {
            'form': form,
            'post_id': post_id,
            'post': instance,
            'creator_profile': creator_profile
        })


# 5. Reader views for newsletters

def newsletter_detail_view(request, slug):
    newsletter = CreatorProfile.objects.get(url_slug=slug)
    is_creator_for_this = False
    template = 'newsletter/newsletter_detail (copy).html'
    if request.user.is_authenticated:
        try:
            if newsletter.user == request.user:
                is_creator_for_this = True
                template = 'newsletter/newsletter_detail_admin.html'
            
            if Subscription.objects.filter(newsletter=newsletter, user=request.user).count() > 0:
                is_subscribed = True
            elif newsletter.user == request.user:
                is_subscribed = True
            else:
                is_subscribed = False
        except:
            is_subscribed = False
    else:
        is_subscribed = False
    try:
        user_profile = get_profile(request.user)
    except:
        user_profile = None

    
    

    stripe.api_key = settings.STRIPE_SECRET_KEY
    publishKey = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        publishKey = settings.STRIPE_PUBLISHABLE_KEY
        token = request.POST.get("stripeToken")
        customer = stripe.Customer.create(
            email=request.user.email,
            source=token,
            stripe_account=newsletter.stripe_account_id,      
            )
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
            {
            "plan": newsletter.stripe_plan_id,
            },
            ],
            stripe_account=newsletter.stripe_account_id,
            )
        subscription_profile = Subscription.objects.create(
            user=request.user,
            newsletter=newsletter,
            stripe_subscription_id=subscription.id,
            stripe_customer_id=customer.id,
            is_active=True)
        user_profile.subscriptions.add(subscription_profile)
        messages.success(request, "You're now subscribed! Go ahead, read some existing posts and expect newsletters arriving to your email inbox.")
        return redirect('newsletter_detail', slug=newsletter.url_slug)
    subscribers = Subscription.objects.filter(newsletter=newsletter)
    newsletter_posts = newsletter.posts.all().order_by('-timestamp')
    page = request.GET.get('page', 1)
    paginator = Paginator(newsletter_posts, 10)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

   
    context = {
        'newsletter': newsletter,
        'newsletter_posts': newsletter_posts,
        'posts': posts,
        'publishKey': publishKey,
        'price': newsletter.price * 100,
        'subscribers': subscribers,
        'is_subscribed': is_subscribed,

    }
    return render(request, template, context)


def newsletter_post_view(request, slug, post_slug):
    newsletter_post = CreatorPost.objects.get(url_slug=post_slug, creatorprofile__url_slug=slug)
    newsletter = CreatorProfile.objects.get(posts=newsletter_post)
    try:
        if Subscription.objects.filter(newsletter=newsletter, user=request.user).count() > 0:
            is_subscribed = True
        elif newsletter.user is request.user:
            is_subscribed = True
        else:
            is_subscribed = False
    except:
        is_subscribed = False


    if len(newsletter_post.video) > 0:
        video = newsletter_post.video
    
        context = {
                'newsletter': newsletter,
                'newsletter_post': newsletter_post,
                'is_subscribed': is_subscribed,
                'video': video,
                
            }
    else:
            context = {
                'newsletter': newsletter,
                'newsletter_post': newsletter_post,
                'is_subscribed': is_subscribed,
       
                
            }

    return render(request, 'newsletter/newsletter_post_detail.html', context)
    

def newsletter_post_subscribe_view(request, slug, post_slug):
    user_profile = Profile.objects.get(user=request.user)
    newsletter = CreatorProfile.objects.get(url_slug=slug)
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        publishKey = settings.STRIPE_PUBLISHABLE_KEY
        token = request.POST.get("stripeToken")
        customer = stripe.Customer.create(
            email=request.user.email,
            source=token,
            stripe_account=newsletter.stripe_account_id,      
            )
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
            {
            "plan": newsletter.stripe_plan_id,
            },
            ],
            stripe_account=newsletter.stripe_account_id,
            )
        subscription_profile = Subscription.objects.create(
            user=request.user,
            newsletter=newsletter,
            stripe_subscription_id=subscription.id,
            stripe_customer_id=customer.id,
            is_active=True)
        user_profile.subscriptions.add(subscription_profile)
        messages.success(request, "You're now subscribed! Go ahead, read some existing posts and expect newsletters arriving to your email inbox.")
        return redirect('newsletter_post_detail', slug=newsletter.url_slug, post_slug=post_slug)


        














@login_required
def newsletter_subscribe_view(request, slug):
    newsletter = CreatorProfile.objects.get(url_slug=slug)

    user_profile = get_profile(request.user)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        token = request.POST['stripeToken']

        customer = stripe.Customer.create(
            email=request.user.email,
            source=token              
            )

        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
            {
                "plan": newsletter.stripe_plan_id,
            },
            ])

        subscription_profile = Subscription.objects.create(
            user=request.user,
            newsletter=newsletter,
            stripe_subscription_id=subscription.id,
            stripe_customer_id=customer.id,
            is_active=True)

        user_profile.subscriptions.add(subscription_profile)

        return redirect('success-subscribed')

    context = {
        'publishKey': publishKey,
        'newsletter': newsletter,
        'price': newsletter.price * 100
    }

    return render(request, "newsletter/newsletter_subscriptions (another copy).html", context)


'''
@login_required
def newsletter_subscribe(request, id):
    newsletter = CreatorProfile.objects.get(id=id)
    #profile = Profile.objects.get(user=request.user)
    user_profile = get_profile(request.user)
    if request.method == 'POST':
        try:
            token = request.POST('stripeToken')
            stripe.Subscription.create(
                customer=customer.id,
                items=[{
                'plan': newsletter.stripe_plan_id,
                }],
                source=token
                )
        except stripe.CardError as e:
            messages.info(request, 'Your card was declined.')
    context = {
        'newsletter': newsletter,
    }
    
    return render(request, 'newsletter/newsletter_signed_up.html', context)
'''
@login_required
def newsletter_unsubscribe(request, slug):
    newsletter = CreatorProfile.objects.get(url_slug=slug)
    user = request.user
    subscription = Subscription.objects.get(newsletter=newsletter, user=user)
    subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
    subscription.delete()
    subscription_to_remove = Subscription.objects.get(newsletter=newsletter, user=user)
    Subscription.delete(subscription_to_remove)
    context = {
        'newsletter': newsletter
    }
    return render(request, 'newsletter/newsletter_unsubscribed.html', context)


@login_required
def subscriptions_view(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'newsletter/newsletter_subscriptions (copy).html', {

            'subscriptions': subscriptions, }
            )

    

class ListSubscribers(APIView):
    def get(self, request, newsletter_id, format=None, many=True):
        subscribers = Subscription.objects.filter(newsletter=newsletter_id)
        timestamps = []
        users = []
        for subscriber in subscribers:
            timestamps.append(subscriber.timestamp)
            users.append(1)
        data = {
        'timestamps': timestamps,
        'subscribers': users
        }
        return Response(data)


def stripe_authorize(request):
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe.client_id = ###

    url = stripe.OAuth.authorize_url(scope='read_write')
    return redirect(url)


def stripe_callback(request):
    import stripe
    creator_profile = CreatorProfile.objects.get(user=request.user)
    from django.http import HttpResponse
    creator_profile = CreatorProfile.objects.get(user=request.user)
    # import requests

    stripe.api_key = settings.STRIPE_SECRET_KEY
    ## import json  # ?

    code = request.GET.get('code', '')
    try:
        resp = stripe.OAuth.token(grant_type='authorization_code', code=code)
    except stripe.oauth_error.OAuthError as e:
        full_response = 'Error: ' + str(e)
        return HttpResponse(full_response)

    creator_profile.stripe_account_id = resp['stripe_user_id']
    product = stripe.Product.create(
            name=creator_profile.name,
            type='service',
            stripe_account=creator_profile.stripe_account_id,
            )
    creator_profile.stripe_product_id = product.id

    plan = stripe.Plan.create(
                product=product.id,
                nickname='Subscription to {}'.format(creator_profile.name),
                interval='month',
                currency='usd',
                amount=creator_profile.price*100,
                stripe_account=creator_profile.stripe_account_id,
                )
    creator_profile.stripe_plan_id = plan.id
    creator_profile.is_active = True
    creator_profile.save()

    full_response = '''
<p>Success! Account <code>{stripe_user_id}</code> is connected.</p>
<p>Click <a href="/stripe-deauthorize?stripe_user_id={stripe_user_id}">here</a> to
disconnect the account.</p>
'''.format(stripe_user_id=resp['stripe_user_id'])
    return HttpResponse(full_response)


def go_to_my_profile(request):
    profile = CreatorProfile.objects.get(user=request.user)
    return redirect('/@{}'.format(profile.url_slug))


