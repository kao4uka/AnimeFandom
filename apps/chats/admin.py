from django.contrib import admin

from apps.chats.models import *

admin.site.register(ChatMessage)


class ChatMessage(admin.TabularInline):
    model = ChatMessage


class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]

    class Meta:
        model = Thread


admin.site.register(Thread, ThreadAdmin)
# admin.site.register(PrivateMessage)
# admin.site.register(FriendRequest)
# admin.site.register(FriendShip)
# admin.site.register(Blacklist)
