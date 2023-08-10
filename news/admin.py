from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import gettext_lazy as _
from .models import Author, Category, Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'author', 'dateCreation', )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )


class FlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': (
                'enable_comments',
                'registration_required',
                'template_name',
            ),
        }),
    )


admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
