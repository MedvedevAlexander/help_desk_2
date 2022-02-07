from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
import os.path
from django.contrib.contenttypes.models import ContentType

from service_objects.services import Service

from .models import Ticket, File


class CheckTicketViewPermissions(Service):
    """
    Проверяет, что пользователь имеет право доступа к текущему тикету.
    К текущему тикету имеют доступ:
    1. Пользователь, создавший тикет
    2. Пользователи, входящие в состав группы 'root_users'
    3. Пользователи, у которых имеются права для доступа к категории тикетов, к которой относится текущий тикет.
    """
    ticket_id = forms.IntegerField()
    user_id = forms.IntegerField()

    def process(self, *args, **kwargs):
        self.ticket_id = self.cleaned_data['ticket_id']
        self.user_id = self.cleaned_data['user_id']

        ticket = Ticket.objects.select_related('category', 'author').get(id=self.ticket_id)
        user = User.objects.get(id=self.user_id)
        user_permissions = user.get_all_permissions()
        ticket_permissions = set(['main.full_access', f'main.can_view_{ticket.category.codename}'])
        permissions_crossing = user_permissions & ticket_permissions

        if not (self.user_id == ticket.author.id or permissions_crossing):
            raise PermissionDenied


def check_ticket_view_permissions(ticket, user):
    return CheckTicketViewPermissions.execute({
        'ticket_id': ticket,
        'user_id': user
    })


class CheckFileDownloadPermissions(Service):
    """
    Проверяет, что пользователь имеет право доступа к текущему файлу.
    К файлу имеют доступ:
    1. пользователь, загрузиваший файл
    2. пользователь, входящий в состав группы 'root_users'
    3. пользователь, входящий в состав группы, обладающей доступом к текущей категории тикетов

    Если прав на доступ нет, вернет 404, но если права есть, ничего не произойдет

    P.S. При проверке прав доступа к файлам считаю, что файл имеет те же параметры доступа, что и тикет, к которому
    он относится. Поэтому проверяю права доступа к тикету, а не к файлу.
    """
    file_link = forms.CharField()
    user_id = forms.IntegerField()

    def process(self):
        self.user_id = self.cleaned_data['user_id']
        self.file_link = self.cleaned_data['file_link']

        file = get_object_or_404(File.objects.select_related('content_type'), file=self.file_link[7:])
        user = User.objects.get(id=self.user_id)

        user_permissions = user.get_all_permissions()
        if file.content_type.name == 'ticket':
            file_permissions = set(['main.full_access', f'main.can_view_{file.content_object.category.codename}'])
        elif file.content_type.name == 'comment':
            file_permissions = set(['main.full_access', f'main.can_view_{file.content_object.ticket.category.codename}'])
        permissions_crossing = user_permissions & file_permissions

        if file.content_type.name == 'ticket':
            if not (self.user_id == file.content_object.author.id or permissions_crossing):
                raise PermissionDenied
        elif file.content_type.name == 'comment':
            if not (self.user_id == file.content_object.ticket.author.id or permissions_crossing):
                raise PermissionDenied


def check_file_download_permissions(file_link, user):
    return CheckFileDownloadPermissions.execute({
        'file_link': file_link,
        'user_id': user.id

    })


"""
def_profile_avatar() - delete all user profile photos from storage and del avatar entry from DB
used when the user uploads new avatar
"""


def del_profile_avatar(user, **kwargs):
    # del file from storage
    user_profile_dir = os.path.join(settings.MEDIA_ROOT, f'user_profile/{user.id}')
    for file in os.listdir(user_profile_dir):
        os.remove(os.path.join(user_profile_dir, file))
    # del file entry in DB
    content_type_id = int(ContentType.objects.get(model='userprofile', app_label='main').id)
    avatars = File.objects.filter(object_id=user.user_profile.id, content_type_id=content_type_id)
    avatars.delete()
