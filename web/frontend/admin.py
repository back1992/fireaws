# -*- coding: utf-8 -*-
from copy import deepcopy
from django.contrib import admin
from mezzanine.blog.admin import BlogPostAdmin
from .models import *

# author_extra_fieldsets = ((None, {"fields": ("dob",)}),)

#
# class BookInline(admin.TabularInline):
#     fields = ('author',)
#     list_display = ('author',)
#     list_display_link = ('author')
#     model = Book


blog_fieldsets = deepcopy(BlogPostAdmin.fieldsets)  # class BookAdmin(admin.ModelAdmin):
blog_fieldsets[0][1]["fields"].insert(-5, "chinese_title")
blog_fieldsets[0][1]["fields"].insert(-5, "author")
blog_fieldsets[0][1]["fields"].insert(-5, "publisher")
blog_fieldsets[0][1]["fields"].insert(-5, "isbn")
blog_fieldsets[0][1]["fields"].insert(-5, "cover")


# blog_fieldsets[0][1]["fields"].insert(-6, "duration")

# class BookResource(resources.ModelResource):
#     class Meta:
#         model = Book



class BookAdmin( BlogPostAdmin):
    # resource_class = BookResource
    fieldsets = blog_fieldsets
    list_display = ('title', 'chinese_title', 'author','status',)
    # list_display_link = ('title', 'npid', 'titlezh',)
    # pass


admin.site.register(Book, BookAdmin)


class AuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(Author, AuthorAdmin)


class PublisherAdmin(admin.ModelAdmin):
    fields = ('name', 'website',)
    list_display = ('name', 'website',)
    list_display_link = ('name')


admin.site.register(Publisher, PublisherAdmin)


class BookCategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(BookCategory, BookCategoryAdmin)


class ChapterAdmin(admin.ModelAdmin):
    list_display = ('no', 'title', 'book', 'audio_file')
    list_filter = ('book',)


admin.site.register(Chapter, ChapterAdmin)
