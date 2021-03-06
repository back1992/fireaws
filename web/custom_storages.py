# custom_storages.py
from django.conf import settings
from s3fs import S3FileSystem, S3File
from storages.backends.s3boto3 import S3Boto3Storage
from storages.backends.s3boto3 import S3Boto3StorageFile


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION

    # def __init__(self, *args, **kwargs):
    #     kwargs["location"] = "media"
    #     kwargs['bucket'] = settings.AWS_STORAGE_BUCKET_NAME
    #     # kwargs['custom_domain'] = domain(settings.MEDIA_URL)
    #     super(MediaStorage, self).__init__(*args, **kwargs)
    #
    # def isfile(self, name):
    #     return self.exists(name)
    #
    # def isdir(self, name):
    #     # That's some inefficient implementation...
    #     # If there are some files having 'name' as their prefix, then
    #     # the name is considered to be a directory
    #     if not name:  # Empty name is a directory
    #         return True
    #
    #     if self.isfile(name):
    #         return False
    #
    #     name = self._normalize_name(self._clean_name(name))
    #     dirlist = self.bucket.list(self._encode_name(name))
    #
    #     # Check whether the iterator is empty
    #     for item in dirlist:
    #         return True
    #     return False
    #
    # def move(self, old_file_name, new_file_name, allow_overwrite=False):
    #
    #     if self.exists(new_file_name):
    #         if allow_overwrite:
    #             self.delete(new_file_name)
    #         else:
    #             raise "The destination file '%s' exists and allow_overwrite is False" % new_file_name
    #
    #     old_key_name = self._encode_name(self._normalize_name(self._clean_name(old_file_name)))
    #     new_key_name = self._encode_name(self._normalize_name(self._clean_name(new_file_name)))
    #
    #     k = self.bucket.copy_key(new_key_name, self.bucket.name, old_key_name)
    #
    #     if not k:
    #         raise "Couldn't copy '%s' to '%s'" % (old_file_name, new_file_name)
    #
    #     self.delete(old_file_name)
    #
    # def makedirs(self, name):
    #     pass
    #
    # def rmtree(self, name):
    #     name = self._normalize_name(self._clean_name(name))
    #     dirlist = self.bucket.list(self._encode_name(name))
    #     for item in dirlist:
    #         item.delete()
    #
    def __init__(self, *args, **kwargs):
        return super(MediaStorage, self).__init__(*args, **kwargs)

    def isfile(self, name):
        try:
            name = self._normalize_name(self._clean_name(name))
            f = S3Boto3StorageFile(name, 'rb', self)
            if not f:
                return False
            return True
        except:
            return False

    def isdir(self, name):
        return not self.isfile(name)

    def isdir(self, name):
        return not self.isfile(name)

    def move(self, old_file_name, new_file_name, allow_overwrite=False):

        if self.exists(new_file_name):
            if allow_overwrite:
                self.delete(new_file_name)
            else:
                raise "The destination file '%s' exists and allow_overwrite is False" % new_file_name

        old_key_name = self._encode_name(self._normalize_name(self._clean_name(old_file_name)))
        new_key_name = self._encode_name(self._normalize_name(self._clean_name(new_file_name)))

        k = self.bucket.copy_key(new_key_name, self.bucket.name, old_key_name)

        if not k:
            raise "Couldn't copy '%s' to '%s'" % (old_file_name, new_file_name)

        self.delete(old_file_name)

    def makedirs(self, name):
        # i can't create dirs still
        pass

    def rmtree(self, name):
        name = self._normalize_name(self._clean_name(name))
        dirlist = self.bucket.list(self._encode_name(name))
        for item in dirlist:
            item.delete()

    def save(self, name, content):
        re = super(MediaStorage, self).save(name, content)
        # key.copy(key.bucket, key.name, preserve_acl=True, metadata={'Content-Type': 'text/plain'})
        return re