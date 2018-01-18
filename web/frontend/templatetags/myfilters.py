# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote, unquote, urlopen
import hashlib

import os
from django.db.models import Q
from future.builtins import str

from collections import defaultdict

from django.core.exceptions import ImproperlyConfigured
from django.template import Context, TemplateSyntaxError, Variable
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

from mezzanine.pages.models import Page
from mezzanine.utils.urls import home_slug
from mezzanine import template
from frontend.models import Book, UserProfile, BookCategory, Chapter, Author
from mezzanine.conf import settings
from mezzanine.generic.models import AssignedKeyword, Keyword
from mezzanine.blog.models import BlogPost, BlogCategory
from django.contrib.auth import get_user_model
from django.db.models import Model, Count
from bs4 import BeautifulSoup

User = get_user_model()

register = template.Library()


@register.as_tag
def chapters_for(value):
    result = Chapter.objects.filter(book_id=value).order_by('no')
    return result


@register.as_tag
def bb_items_for(value, no=1):
    """
    Return a list of ``Keyword`` objects for the given model instance
    or a model class. In the case of a model class, retrieve all
    keywords for all instances of the model and apply a ``weight``
    attribute that can be used to create a tag cloud.
    """
    data = Chapter.objects.filter(book_id=value).order_by('no')[no - 1]
    # # parsing the text
    n = 500
    words = iter(data.content.split())
    lines, current = [], next(words)
    for word in words:
        if len(current) + 1 + len(word) > n:
            soup = BeautifulSoup(current, "html.parser")
            current = soup.prettify()
            lines.append(current)
            current = word
        else:
            current += " " + word
    lines.append(current)
    return lines


@register.as_tag
def blog_recent_books(limit=5, tag=None, username=None, category=None):
    """
    Put a list of recently published blog posts into the template
    context. A tag title or slug, category title or slug or author's
    username can also be specified to filter the recent posts returned.

    Usage::

        {% blog_recent_posts 5 as recent_posts %}
        {% blog_recent_posts limit=5 tag="django" as recent_posts %}
        {% blog_recent_posts limit=5 category="python" as recent_posts %}
        {% blog_recent_posts 5 username=admin as recent_posts %}

    """
    # blog_posts = Book.objects.published().select_related("user")
    blog_posts = Book.objects.select_related("user")
    title_or_slug = lambda s: Q(title=s) | Q(slug=s)
    if tag is not None:
        try:
            tag = Keyword.objects.get(title_or_slug(tag))
            blog_posts = blog_posts.filter(keywords__keyword=tag)
        except Keyword.DoesNotExist:
            return []
    if category is not None:
        try:
            category = BlogCategory.objects.get(title_or_slug(category))
            blog_posts = blog_posts.filter(categories=category)
        except BlogCategory.DoesNotExist:
            return []
    if username is not None:
        try:
            author = User.objects.get(username=username)
            blog_posts = blog_posts.filter(user=author)
        except User.DoesNotExist:
            return []
    return list(blog_posts[:limit])


@register.as_tag
def book_categories(*args):
    """
    Put a list of categories for blog posts into the template context.
    """
    # posts = Book.objects.published()
    posts = Book.objects.all()
    categories = BookCategory.objects.filter(blogposts__in=posts)
    return list(categories.annotate(post_count=Count("blogposts")))


@register.filter(name='get_cover')
def get_cover(value):
    result = Book.objects.get(blogpost_ptr_id=value)
    return result.cover


@register.filter(name='get_cover_url')
def get_cover_url(value):
    # blog_post = BlogPost.objects.get(title=value)
    if value.featured_image:
        return value.featured_image.url
    else:
        result = Book.objects.get(blogpost_ptr_id=value.id)
        if result.cover:
            return result.cover.url
        else:
            return "/avatar/firefly-insect-clipart-downloads-e5tSeV-clipart.png"

@register.filter(name='get_chinese_title')
def get_chinese_title(value):
    result = Book.objects.get(blogpost_ptr_id=value.id)
    return result.chinese_title


@register.filter(name='get_author')
def get_author(value):
    book = Book.objects.get(blogpost_ptr_id=value)
    try:
        author = Author.objects.get(id=book.author_id)
        return author.chinese_name + '/' + author.english_name
    except:
        return ''

    # return getattr(author, name)



@register.render_tag
def my_page_menu(context, token):
    """
    Return a list of child pages for the given parent, storing all
    pages in a dict in the context when first called using parents as keys
    for retrieval on subsequent recursive calls from the menu template.
    """
    # First arg could be the menu template file name, or the parent page.
    # Also allow for both to be used.
    template_name = None
    parent_page = None
    parts = token.split_contents()[1:]
    for part in parts:
        part = Variable(part).resolve(context)
        if isinstance(part, str):
            template_name = part
        elif isinstance(part, Page):
            parent_page = part
    if template_name is None:
        try:
            template_name = context["menu_template_name"]
        except KeyError:
            error = "No template found for page_menu in: %s" % parts
            raise TemplateSyntaxError(error)
    context["menu_template_name"] = template_name
    if "menu_pages" not in context:
        try:
            user = context["request"].user
            slug = context["request"].path
        except KeyError:
            user = None
            slug = ""
        num_children = lambda id: lambda: len(context["menu_pages"][id])
        has_children = lambda id: lambda: num_children(id)() > 0
        rel = [m.__name__.lower()
               for m in Page.get_content_models()
               if not m._meta.proxy]
        published = Page.objects.published(for_user=user).select_related(*rel)
        # Store the current page being viewed in the context. Used
        # for comparisons in page.set_menu_helpers.
        if "page" not in context:
            try:
                context.dicts[0]["_current_page"] = published.exclude(
                    content_model="link").get(slug=slug)
            except Page.DoesNotExist:
                context.dicts[0]["_current_page"] = None
        elif slug:
            context.dicts[0]["_current_page"] = context["page"]
        # Some homepage related context flags. on_home is just a helper
        # indicated we're on the homepage. has_home indicates an actual
        # page object exists for the homepage, which can be used to
        # determine whether or not to show a hard-coded homepage link
        # in the page menu.
        home = home_slug()
        context.dicts[0]["on_home"] = slug == home
        context.dicts[0]["has_home"] = False
        # Maintain a dict of page IDs -> parent IDs for fast
        # lookup in setting page.is_current_or_ascendant in
        # page.set_menu_helpers.
        context.dicts[0]["_parent_page_ids"] = {}
        pages = defaultdict(list)
        for page in published.order_by("_order"):
            page.set_helpers(context)
            context["_parent_page_ids"][page.id] = page.parent_id
            setattr(page, "num_children", num_children(page.id))
            setattr(page, "has_children", has_children(page.id))
            pages[page.parent_id].append(page)
            if page.slug == home:
                context.dicts[0]["has_home"] = True
        # Include menu_pages in all contexts, not only in the
        # block being rendered.
        context.dicts[0]["menu_pages"] = pages
    # ``branch_level`` must be stored against each page so that the
    # calculation of it is correctly applied. This looks weird but if we do
    # the ``branch_level`` as a separate arg to the template tag with the
    # addition performed on it, the addition occurs each time the template
    # tag is called rather than once per level.
    context["branch_level"] = 0
    parent_page_id = None
    if parent_page is not None:
        context["branch_level"] = getattr(parent_page, "branch_level", 0) + 1
        parent_page_id = parent_page.id

    # Build the ``page_branch`` template variable, which is the list of
    # pages for the current parent. Here we also assign the attributes
    # to the page object that determines whether it belongs in the
    # current menu template being rendered.
    context["page_branch"] = context["menu_pages"].get(parent_page_id, [])
    context["page_branch_in_menu"] = False
    # context["icon_in_menu"] = {"1": "disk", "2": "music-tone-alt", "3": "drawer", "4": "list", "5": "music-tone",
    #                            "6": "grid", "7": "screen-desktop", "8": "playlist"}
    context["icon_in_menu"] = ["disk", "music-tone-alt", "drawer", "list", "music-tone",
                               "grid", "screen-desktop", "playlist"]
    for page in context["page_branch"]:
        page.in_menu = page.in_menu_template(template_name)
        page.num_children_in_menu = 0
        if page.in_menu:
            context["page_branch_in_menu"] = True
        for child in context["menu_pages"].get(page.id, []):
            if child.in_menu_template(template_name):
                page.num_children_in_menu += 1
        page.has_children_in_menu = page.num_children_in_menu > 0
        page.branch_level = context["branch_level"]
        page.parent = parent_page
        context["parent_page"] = page.parent

        # Prior to pages having the ``in_menus`` field, pages had two
        # boolean fields ``in_navigation`` and ``in_footer`` for
        # controlling menu inclusion. Attributes and variables
        # simulating these are maintained here for backwards
        # compatibility in templates, but will be removed eventually.
        page.in_navigation = page.in_menu
        page.in_footer = not (not page.in_menu and "footer" in template_name)
        if page.in_navigation:
            context["page_branch_in_navigation"] = True
        if page.in_footer:
            context["page_branch_in_footer"] = True

    t = get_template(template_name)
    return t.render(Context(context))


@register.simple_tag(takes_context=True)
def my_fields_for(context, form, template="includes/my_form_fields.html"):
    """
    Renders fields for a form with an optional template choice.
    """
    context["form_for_fields"] = form
    return get_template(template).render(context)



@register.simple_tag
def my_gravatar_url(email, size=32):
    """
    Return the full URL for a Gravatar given an email hash.
    """
    # bits = (md5(email.lower().encode("utf-8")).hexdigest(), size)
    # return "//www.gravatar.com/avatar/%s?s=%s&d=identicon&r=PG" % bits

    # user = User.model(email=email, is_staff=False, is_active=True, **extra_fields)
    try:
        user = User.objects.get(email=email)
        avatar = str(user.profile.avatar)
        media_url = settings.MEDIA_URL
        avatar = media_url + '/' + avatar
        return avatar
    except:
        bits = (hashlib.md5(email.lower().encode("utf-8")).hexdigest(), size)
        return "//www.gravatar.com/avatar/%s?s=%s&d=identicon&r=PG" % bits

@register.filter
def shuffle(arg):
    tmp = list(arg)[:]
    random.shuffle(tmp)
    return tmp