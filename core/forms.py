from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CreatorProfile, CreatorPost, CustomUser
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, ButtonHolder, Submit
from crispy_forms.bootstrap import AppendedText, PrependedText
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser




class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None


    helper = FormHelper()
    helper.form_class = 'form-group'
    helper.layout = Layout(

        Field('username', css_class='form-control')
        )

    widgets = {
            'username' : forms.TextInput(attrs = {'placeholder': 'JohnAwesome'}),
           
           
        }

class CreatorProfileCreateForm(forms.ModelForm):
    class Meta:
        model = CreatorProfile
        fields = ('name','description', 'price', 'cover_pic' )
        labels = {
        "name": "Name of your creator profile",
    }

class CreatorProfileEditForm(forms.ModelForm):
    class Meta:
        model = CreatorProfile
        fields = ('name','description','cover_pic',)
        labels = {
        "name": "Newsletter Name",
        }


class CreatorPostForm(forms.ModelForm):
    #MY_CHOICES =    (
     #   (False, 'Only send to subscribers'),
     #   (True, 'Make public online')
    #    )
   # is_public = forms.ChoiceField(choices=MY_CHOICES, widget=forms.RadioSelect(), label="Set publicity:")

    class Meta:
        model = CreatorPost
        fields = ('title', 'content', 'featured_image', 'publicity')
        widgets = {
        'title': forms.TextInput(attrs={'class':'form-control'})
        }
    '''   CHOICES = [
    (False, 'Only send to subscribers'),
    (True, 'Make public to everyone online')
    ]
    is_public = forms.ChoiceField(choices=CHOICES, label="Where do you want to publish?")'''



#class UserForm(forms.ModelForm):
 #   class Meta:
   #     model = User

