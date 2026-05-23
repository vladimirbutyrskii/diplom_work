from django.contrib import admin

from .models import Ad, Comment


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('text',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
