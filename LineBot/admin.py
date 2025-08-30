from django.contrib import admin
from .models import User, Group

# Register your models here.
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'number')
    search_fields = ('company', 'number')
    ordering = ('company', 'number')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user_name', 'department', 'group')
    search_fields = ('user_id', 'user_name', 'department', 'group')
    ordering = ('user_name', 'group')