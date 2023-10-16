from django.contrib import admin
from apps.friends.models import *


class FriendListAdmin(admin.ModelAdmin):
    list_display = ['user']
    list_filter = ['user']
    search_fields = ['user']

    class Meta:
        model = FriendList


admin.site.register(FriendList, FriendListAdmin)


class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ['sender', 'receiver']
    list_display = ['sender', 'receiver']
    search_fields = ['sender__username', 'receiver__username']
    readonly_fields = ['id']

    class Meta:
        model = FriendRequest


admin.site.register(FriendRequest, FriendRequestAdmin)