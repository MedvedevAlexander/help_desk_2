from django.contrib import admin
from .models import TicketCategory, TicketStatus, TicketPriority
from django.contrib.admin import StackedInline


class TicketPriorityAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class TicketStatusAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename')
    search_fields = ('name', 'codename')


admin.site.register(TicketCategory, TicketCategoryAdmin)
admin.site.register(TicketStatus, TicketStatusAdmin)
admin.site.register(TicketPriority, TicketPriorityAdmin)
