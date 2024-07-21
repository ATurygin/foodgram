from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'date_joined', 'is_staff',
                    'avatar',)
    list_editable = ('avatar', 'is_staff',)
    search_fields = ('username', 'email')
    date_hierarchy = 'date_joined'


admin.site.register(User, UserAdmin)
