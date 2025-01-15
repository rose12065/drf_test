from django.contrib import admin

from .models import APILog, CustomUser, Item

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Item)
admin.site.register(APILog)