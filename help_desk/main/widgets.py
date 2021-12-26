from django.forms import Textarea, TextInput, Select, ClearableFileInput, EmailInput, PasswordInput


class TextareaBootstrap(Textarea):
    def __init__(self, placeholder=''):
        super(TextareaBootstrap, self).__init__()
        self.attrs = {
            'class': 'form-control',
            'rows': '3',
            'placeholder': placeholder,
            'style': 'margin-top: 0px; margin-bottom: 0px; height: 210px;'
        }


class TextInputBootstrap(TextInput):
    def __init__(self, placeholder=''):
        super(TextInputBootstrap, self).__init__()
        self.attrs = {
            'class': 'form-control',
            'placeholder': placeholder
        }


class SelectBootstrap(Select):
    def __init__(self):
        super(SelectBootstrap, self).__init__()
        self.attrs = {
            'class': 'custom-select'
        }


class ClearableFileInputBootstrap(ClearableFileInput):
    def __init__(self):
        super(ClearableFileInput, self).__init__()
        self.attrs = {
            'class': 'form-control',
            'multiple': True
        }


class EmailFieldBootstrap(EmailInput):
    def __init__(self, placeholder=''):
        super(EmailFieldBootstrap, self).__init__()
        self.attrs = {
            'class': 'form-control',
            'placeholder': placeholder
        }


class PasswordInputBootstrap(PasswordInput):
    def __init__(self, placeholder=''):
        super(PasswordInputBootstrap, self).__init__()
        self.attrs = {
            'class': 'form-control',
            'placeholder': placeholder
        }
