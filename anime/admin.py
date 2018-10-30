from django.contrib import admin

# Register your models here.
from anime.models import Anime, Studio, User, Tag, Episode

admin.site.register(Anime)
admin.site.register(Studio)
admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Episode)