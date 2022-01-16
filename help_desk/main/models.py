from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class News(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    added_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-added_at']


class TicketPriority(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Приоритеты заявок'


class TicketCategory(models.Model):
    name = models.TextField(max_length=255)
    codename = models.TextField(max_length=255, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Категории заявок'


class TicketStatus(models.Model):
    name = models.TextField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Статусы заявок'


class Ticket(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    added_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ticket_author')
    category = models.ForeignKey(TicketCategory, on_delete=models.SET_NULL, null=True, related_name='ticket_category')
    priority = models.ForeignKey(TicketPriority, on_delete=models.SET_NULL, null=True, related_name='ticket_priority')
    status = models.ForeignKey(TicketStatus, on_delete=models.SET_NULL, null=True, related_name='ticket_status')
    files = GenericRelation('File')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Заявки'
        ordering = ['-added_at']


class Comment(models.Model):
    text = models.TextField()
    added_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comment_author')
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, related_name='comment_ticket')
    files = GenericRelation('File')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-added_at']


""" 
Class File - класс с полиморфной связью

Поля file и file_name необходимы т.к. при загрузке в рамках одного тикета файлов с одинаковым
именем в директорию они будут сохраняться под разными именами. 
Чтобы отдать файл пользователю, используем поле file. 
Чтобы отобразить ссылку с именем файла, заданным пользователем, используем file_name.

В последствии пришел к выводу, что не стоило менять первоначальный вариант модели File, где использовались
NULL поля, в пользу GenericForeignKey, т.к. это создает некоторые сложности (дополнительные запросы к БД,
вероятность нарушения ссылочной целостности, усложнение структуры БД).
Назад возвращать не стал, т.к. проект тестовый, решил оставить, чтобы был в будущем пример как делать не стоит
Хорошая статья про GenericForeignKey: https://djbook.ru/examples/88/
"""


class File(models.Model):
    def get_file_path(self, *args, **kwargs):
        if self.content_type.name == 'ticket':
            return f'ticket_attachments/{self.content_object.id}/{self.file.name}'
        elif self.content_type.name == 'comment':
            return f'ticket_attachments/{self.content_object.ticket.id}/{self.file.name}'

    file = models.FileField(blank=True, upload_to=get_file_path)
    file_name = models.CharField(max_length=255, null=True)
    file_size = models.IntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')


class UserProfile(models.Model):
    organization = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    photo = GenericRelation('File')
