from django.conf import settings
from django.db import models


class Presentation(models.Model):
    name = models.CharField(max_length=60)
    summary = models.TextField()
    speaker = models.ForeignKey(settings.AUTH_USER_MODEL)

    @models.permalink
    def get_absolute_url(self):
        return ('presentations',)

    def __unicode__(self):
        return self.name
