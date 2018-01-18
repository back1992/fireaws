# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import *
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from mezzanine.generic.models import Keyword
from calendar import month_name
from django.http import Http404
from django.contrib.auth import get_user_model
from mezzanine.utils.views import paginate
from mezzanine.conf import settings
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


def index(request, tag=None, year=None, month=None, username=None,
          category=None, template="frontend/index.html",
          extra_context=None):
    """
    Display a list of blog posts that are filtered by tag, year, month,
    author or category. Custom templates are checked for using the name
    ``blog/blog_post_list_XXX.html`` where ``XXX`` is either the
    category slug or author's username if given.
    """
    templates = []
    blog_posts = Book.objects.published(for_user=request.user).order_by('?')[:12]
    # blog_posts = Book.objects.published().order_by('?')[:12]
    if tag is not None:
        tag = get_object_or_404(Keyword, slug=tag)
        blog_posts = blog_posts.filter(keywords__keyword=tag)
    if year is not None:
        blog_posts = blog_posts.filter(publish_date__year=year)
        if month is not None:
            blog_posts = blog_posts.filter(publish_date__month=month)
            try:
                month = _(month_name[int(month)])
            except IndexError:
                raise Http404()
    if category is not None:
        category = get_object_or_404(BookCategory, slug=category)
        blog_posts = blog_posts.filter(categories=category)
        templates.append(u"frontend/book_list_%s.html" %
                         str(category.slug))
    author = None
    if username is not None:
        author = get_object_or_404(User, username=username)
        blog_posts = blog_posts.filter(user=author)
        templates.append(u"frontend/book_list_%s.html" % username)

    prefetch = ("categories", "keywords__keyword")
    blog_posts = blog_posts.select_related("user").prefetch_related(*prefetch)
    blog_posts = paginate(blog_posts, request.GET.get("page", 1),
                          settings.BLOG_POST_PER_PAGE,
                          settings.MAX_PAGING_LINKS)
    context = {"blog_posts": blog_posts, "year": year, "month": month,
               "tag": tag, "category": category, "author": author}
    context.update(extra_context or {})
    templates.append(template)
    return TemplateResponse(request, templates, context)
