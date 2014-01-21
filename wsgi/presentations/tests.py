from django.test import TestCase

from .models import Presentation


class PresentationTest(TestCase):
    def test_unicode(self):
        presentation = Presentation(name="My presentation")
        self.assertEquals("My presentation", unicode(presentation))
