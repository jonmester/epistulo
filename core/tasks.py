from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context, Template
from django.template.loader import render_to_string
from .models import User, NewsletterProfile, Subscription
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task
def send_newsletters(instance, newsletter):
    subscribers = Subscription.objects.filter(newsletter=newsletter)
    subscriber_list = []
    for subscriber in subscribers:
            subscriber_list.append(subscriber.user.email)

    subject = instance.title
    from_email = '{}<jonmester3@gmail.com>'.format(newsletter.name)
    to = subscriber_list
    html_message = instance.content
    plain_message = strip_tags(instance.content)
    context = {
    'title': subject,
    'content': html_message,
    'newsletter': newsletter,
    }

    html_body = render_to_string("email/index.html", context)

    email = EmailMultiAlternatives(subject, plain_message, from_email, to)
    email.attach_alternative(html_body, 'text/html')
    email.send()