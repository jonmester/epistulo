"""epistulo_2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
import anymail
from django.urls import path
from django.contrib import admin
from django.urls import path, include, re_path
from core import views
from core.views import ListSubscribers
from django.conf import settings

from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('discover', views.discover_view, name='discover'),
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('signup/<slug:slug>', views.signup_redirect, name='signup-redirect'),
    path('newsletter/create', views.newsletter_create, name='create'),
    path('newsletter/admin', views.newsletter_admin, name='newsletter_admin'),
    path('newsletter/admin/edit-profile', views.newsletter_edit_profile, name='edit-profile'),
    path('newsletter/admin/delete-profile', views.newsletter_delete_profile, name='delete-profile'),
    path('newsletter/admin/write-post', views.newsletter_write, name='write-post'),
    path('newsletter/admin/delete-<int:post_id>', views.newsletter_delete_post, name='delete-post'),
    path('newsletter/admin/edit-<int:post_id>', views.newsletter_edit, name='edit-post'),

    path('@<slug:slug>', views.newsletter_detail_view, name='newsletter_detail'),
    path('@<slug:slug>/<int:modal>', views.newsletter_detail_view, name='newsletter_detail_modal'),
    path('@<slug:slug>/<slug:post_slug>', views.newsletter_post_view, name='newsletter_post_detail'),
    path('@<slug:slug>/<slug:post_slug>/subscribe', views.newsletter_post_subscribe_view, name='newsletter_post_subscribe'),
    path('@<slug:slug>/subscribe/', views.newsletter_subscribe_view, name='subscribe-to-newsletter'),
   # path('read/<slug:post_slug>-<int:post_id>', views.newsletter_post_view, name='newsletter_post_detail'),
    path('newsletter/admin/ch-<slug:post_slug>-<int:post_id>', views.change_publicity_state, name='change_publicity_state'),
    path('@<slug:slug>/unsubscribe', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('success/', views.home, name='success-subscribed'),
    path('user/subscriptions', views.subscriptions_view, name='subscriptions'),
    #path('ckeditor/', ckeditor_uploader.urls),
    #path('anymail/', anymail.urls),
    path('api/subscribers/data/<int:newsletter_id>', ListSubscribers.as_view(), name='api-data'),

    re_path(r'^oauth/', include('social_django.urls', namespace='social')),
    re_path(r'^password/$', views.change_password, name='change_password'),
    path('connect/stripe', views.stripe_authorize, name='connect-stripe'),
    path('connect/stripe-callback', views.stripe_callback, name='callback-stripe'),
    path('goto-profile', views.go_to_my_profile, name='go-to-profile'),
    path('logout', views.logout_view, name='logout'),
    


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)