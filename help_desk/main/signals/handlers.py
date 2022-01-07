from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from main.models import TicketCategory, Ticket, Comment


@receiver(post_save, sender=TicketCategory)
def create_group(sender, **kwargs):
    Group.objects.create(name=f'{kwargs["instance"].codename}_admins')
