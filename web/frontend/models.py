# -*- coding: utf-8 -*-
import os
from django.db import models
from mezzanine.blog.models import BlogCategory, BlogPost
from mezzanine.core.fields import RichTextField
from mezzanine.conf import settings
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.managers import SearchableManager


class Author(models.Model):
    english_name = models.CharField(max_length=30, null=True, verbose_name=u"英文姓名", unique=True)
    chinese_name = models.CharField(max_length=40, null=True, verbose_name=u"中文姓名")
    country = models.CharField(max_length=40, null=True, verbose_name=u"国家")
    description = models.TextField(verbose_name=u"作者简介", null=True)

    objects = SearchableManager()
    search_fields = ("english_name", "chinese_name")

    def __str__(self):
        return self.english_name + '---' + self.chinese_name

    class Meta:
        verbose_name = u'作者'
        verbose_name_plural = u'作者'


class BookCategory(BlogCategory):
    image = models.ImageField(upload_to="categories", verbose_name=u"图片", null=True)

    class Meta:
        verbose_name = u'书籍分类'
        verbose_name_plural = u'书籍分类'

    def __str__(self):
        return str(self.title)


BookCategory._meta.get_field('title').verbose_name = u'分类名称'


class Publisher(models.Model):
    name = models.CharField(max_length=30, verbose_name=u"名称")
    website = models.URLField(verbose_name=u"网址")

    def __str__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = u'出版社'
        verbose_name_plural = u'出版社'


class Book(BlogPost):
    chinese_title = models.CharField(max_length=100, null=True, verbose_name=u"中文书名")
    isbn = models.CharField(max_length=100, null=True, verbose_name="ISBN")
    author = models.ForeignKey("Author", verbose_name=u"作者")
    publisher = models.ForeignKey(Publisher, null=True, verbose_name=u"出版社")
    publication_date = models.DateField(null=True, verbose_name=u"出版日期")
    cover = models.FileField(upload_to="covers", verbose_name=u"图片", null=True)
    # cover = ThumbnailerImageField(upload_to="covers", verbose_name=u"图片", null=True)
    # photo = ThumbnailerImageField(upload_to='cover_photos', blank=True)

    objects = SearchableManager()
    search_fields = ("title", "description")

    class Meta:
        verbose_name = u'图书'
        verbose_name_plural = u'图书'


Book._meta.get_field('title').verbose_name = u'英文书名'
# Book._meta.get_field('featured_image').verbose_name = u'封面图片'
Book._meta.get_field('categories').verbose_name = u'目录'
Book._meta.get_field('content').verbose_name = u'内容简介'


class Chapter(models.Model):
    no = models.IntegerField(db_index=True)
    title = models.CharField(max_length=100, null=True, verbose_name=u"章节标题")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name=u"所属书籍")
    content = RichTextField(_("Content"))
    audio_file = models.FileField(upload_to="audio_file", blank=True,
                                  help_text="Allowed type - .mp3, .wav, .ogg", verbose_name=u"音频文件")

    #
    # # Add this method to your model
    # def audio_file_player(self):
    #     """audio player tag for admin"""
    #     if self.audio_file:
    #         file_url = settings.MEDIA_URL + str(self.audio_file)
    #         player_string = '<ul class="playlist"><li style="width:250px;">\
    #         <a href="%s">%s</a></li></ul>' % (file_url, os.path.basename(self.audio_file.name))
    #         return player_string
    #
    # audio_file_player.allow_tags = True
    # audio_file_player.short_description = u'音频文件'

    def __str__(self):
        return "%s: 第%s章节" % (self.book.title, self.no)
        # this is not needed if small_image is created at set_image

    def save(self, *args, **kwargs):
        self.max_length = None
        super(Chapter, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'章节管理'
        verbose_name_plural = u'章节管理'


class UserProfile(models.Model):
    user = models.OneToOneField("auth.User", related_name='profile')
    avatar = models.ImageField(upload_to='avatar', blank=True)
    # avatar = ThumbnailerImageField(upload_to='avatar', blank=True)
    # photo = ThumbnailerImageField(upload_to='user_photos', blank=True)
    # photo = ImageField(upload_to='user_photos', blank=True)
    bio = models.TextField(blank=True)

    # address = models.OneToOneField("Address", null=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = u'会员管理'
        verbose_name_plural = u'会员管理'
