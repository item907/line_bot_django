from django.contrib import admin

# Register your models here.
from line.models import *

class TextChatAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'chatword', 'isword')

admin.site.register(TextChat, TextChatAdmin)