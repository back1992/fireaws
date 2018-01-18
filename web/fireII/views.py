# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from frontend.models import *
from django.template.response import TemplateResponse
from django.contrib.auth import get_user_model
from mezzanine.utils.views import paginate, is_spam, set_cookie
from mezzanine.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.apps import apps
from mezzanine.core.models import Displayable, SitePermission
from django.db.models import Q

User = get_user_model()


def search(request, template="search_results.html", extra_context=None):
    """
    Display search results. Takes an optional "contenttype" GET parameter
    in the form "app-name.ModelName" to limit search results to a single model.
    """
    query = request.GET.get("q", "")
    page = request.GET.get("page", 1)
    per_page = settings.SEARCH_PER_PAGE
    max_paging_links = settings.MAX_PAGING_LINKS
    try:
        parts = request.GET.get("type", "").split(".", 1)
        search_model = apps.get_model(*parts)
        search_model.objects.search  # Attribute check
    except (ValueError, TypeError, LookupError, AttributeError):
        search_model = Displayable
        search_type = _("Everything")
    else:
        search_type = search_model._meta.verbose_name_plural.capitalize()
    results = search_model.objects.search(query, for_user=request.user)
    queryTitle = query.split("‧", 1);

    results_title =  list(Book.objects.filter(Q(title__contains=query) | Q(chinese_title__contains=queryTitle[0])))
    author = Author.objects.filter(Q(chinese_name__contains=query) | Q(english_name__contains=query)).first()
    results_author = []
    if author:
        results_author = list(Book.objects.filter(author_id=author.id))

    results = list(set(results + results_author+ results_title))
    paginated = paginate(results, page, per_page, max_paging_links)
    context = {"query": query, "results": paginated,
               "search_type": search_type}
    context.update(extra_context or {})
    return TemplateResponse(request, template, context)

# def search(request, template="search_results.html", extra_context=None):
#     """
#     Display search results. Takes an optional "contenttype" GET parameter
#     in the form "app-name.ModelName" to limit search results to a single model.
#     """
#     query = request.GET.get("q", "")
#     page = request.GET.get("page", 1)
#     per_page = settings.SEARCH_PER_PAGE
#     max_paging_links = settings.MAX_PAGING_LINKS
#     try:
#         parts = request.GET.get("type", "").split(".", 1)
#         search_model = apps.get_model(*parts)
#         search_model.objects.search  # Attribute check
#     except (ValueError, TypeError, LookupError, AttributeError):
#         search_model = Displayable
#         search_type = _("Everything")
#     else:
#         search_type = search_model._meta.verbose_name_plural.capitalize()
#     results = search_model.objects.search(query, for_user=request.user)
#     queryTitle = query.split("‧", 1);
#
#     results_title =  list(Book.objects.filter(Q(title__contains=query) | Q(titlezh__contains=queryTitle[0])))
#     author = Author.objects.filter(Q(chinese_name__contains=query) | Q(english_name__contains=query)).first()
#     results_author = []
#     if author:
#         results_author = list(Book.objects.filter(author_id=author.id))
#
#     results = list(set(results + results_author+ results_title))
#
#     paginated = paginate(results, page, per_page, max_paging_links)
#     context = {"query": query, "results": paginated,
#                "search_type": search_type}
#     context.update(extra_context or {})
#     return TemplateResponse(request, template, context)

# def index(request, tag=None, year=None, month=None, username=None,
#           category=None, template="frontend/index.html",
#           extra_context=None):
#     """
#     Display a list of blog posts that are filtered by tag, year, month,
#     author or category. Custom templates are checked for using the name
#     ``blog/blog_post_list_XXX.html`` where ``XXX`` is either the
#     category slug or author's username if given.
#     """
#     templates = []
#     # blog_posts = BlogPost.objects.published(for_user=request.user)
#     blog_posts = Book.objects.published(for_user=request.user).order_by('?')[:12]
#     if tag is not None:
#         tag = get_object_or_404(Keyword, slug=tag)
#         blog_posts = blog_posts.filter(keywords__keyword=tag)
#     if year is not None:
#         blog_posts = blog_posts.filter(publish_date__year=year)
#         if month is not None:
#             blog_posts = blog_posts.filter(publish_date__month=month)
#             try:
#                 month = _(month_name[int(month)])
#             except IndexError:
#                 raise Http404()
#     if category is not None:
#         category = get_object_or_404(BookCategory, slug=category)
#         blog_posts = blog_posts.filter(categories=category)
#         templates.append(u"frontend/book_list_%s.html" %
#                          str(category.slug))
#     author = None
#     if username is not None:
#         author = get_object_or_404(User, username=username)
#         blog_posts = blog_posts.filter(user=author)
#         templates.append(u"frontend/book_list_%s.html" % username)
#
#     prefetch = ("categories", "keywords__keyword")
#     blog_posts = blog_posts.select_related("user").prefetch_related(*prefetch)
#     blog_posts = paginate(blog_posts, request.GET.get("page", 1),
#                           settings.BLOG_POST_PER_PAGE,
#                           settings.MAX_PAGING_LINKS)
#     context = {"blog_posts": blog_posts, "year": year, "month": month,
#                "tag": tag, "category": category, "author": author}
#     context.update(extra_context or {})
#     templates.append(template)
#     return TemplateResponse(request, templates, context)
#
#
