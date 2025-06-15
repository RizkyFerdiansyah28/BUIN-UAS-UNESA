from django.contrib import admin
from .models import DimGenre, DimActor, DimTime, FactMovie

# Mendaftarkan model agar muncul di halaman admin
@admin.register(DimGenre)
class DimGenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'genre_name')

@admin.register(DimActor)
class DimActorAdmin(admin.ModelAdmin):
    list_display = ('id', 'actor_name')
    search_fields = ('actor_name',)

@admin.register(DimTime)
class DimTimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'release_year')
    ordering = ('-release_year',)

@admin.register(FactMovie)
class FactMovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'actor', 'genre', 'time', 'rating', 'votes')
    list_filter = ('genre', 'time')
    search_fields = ('title', 'actor__actor_name', 'genre__genre_name')