from django.contrib import admin
from .models import Todo

admin.site.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['title', 'column', 'position', 'created_in']
    list_editable = ['column', 'position']   