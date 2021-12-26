from django.forms import ModelForm, Textarea, HiddenInput, inlineformset_factory, Form
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User


from .models import Ticket, Comment, UserAccount, File
from .widgets import TextareaBootstrap, TextInputBootstrap, SelectBootstrap, ClearableFileInputBootstrap, \
    EmailFieldBootstrap, PasswordInputBootstrap


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'text', 'category', 'priority', 'author']
        widgets = {
            'text': TextareaBootstrap(placeholder='Describe your problem'),
            'title': TextInputBootstrap(placeholder='Brief describe of your problem'),
            'category': SelectBootstrap(),
            'priority': SelectBootstrap(),
            'author': HiddenInput()
        }
        labels = {
            'title': 'Theme'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'ticket', 'user']
        widgets = {
            'text': TextareaBootstrap(placeholder='Enter your message')
        }


class UploadFileForm(ModelForm):
    class Meta:
        model = File
        fields = ['file']
        widgets = {
            'file': ClearableFileInputBootstrap()
        }


class SignupForm(forms.Form):
    username = forms.CharField(max_length=50, widget=TextInputBootstrap(placeholder='Enter username'))
    email = forms.EmailField(widget=EmailFieldBootstrap(placeholder='Enter you e-mail address'))
    password_1 = forms.CharField(max_length=30, widget=PasswordInputBootstrap(placeholder='Enter you password'))
    password_2 = forms.CharField(max_length=30, widget=PasswordInputBootstrap(placeholder='Repeat you password'))

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('User with this name is already registered', code='user_already_exists')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            email = User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('The specified email is already registered', code='email_already_exists')

    def clean(self):
        password_1 = self.cleaned_data['password_1']
        password_2 = self.cleaned_data['password_2']
        if password_1 != password_2:
            raise forms.ValidationError('Password mismatch', code='password_mismatch')
        return self.cleaned_data

    def save(self, *args, **kwargs):
        user = User.objects.create_user(username=self.cleaned_data['username'],
                                        email=self.cleaned_data['email'],
                                        password=self.cleaned_data['password_1'])
        return user


class UserAccountAdditionalForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = ['organization', 'city', 'position', 'phone']


class UserAccountForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ['password']
