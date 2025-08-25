from django.contrib import admin
from .models import EKA

class EKAAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname", "phone", "joined_date")
admin.site.register(EKA, EKAAdmin)
