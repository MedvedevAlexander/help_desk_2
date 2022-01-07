from django.contrib import admin
from .models import TicketCategory, Ticket, Comment
from django.contrib.admin import StackedInline


class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename')
    list_editable = ('codename',)
    search_fields = ('name', 'codename')


admin.site.register(TicketCategory, TicketCategoryAdmin)
