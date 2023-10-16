from django.contrib import admin
from apps.anime.models import *

admin.site.register(Genre)
admin.site.register(Tag)
admin.site.register(Anime)
admin.site.register(Season)
admin.site.register(Episode)
