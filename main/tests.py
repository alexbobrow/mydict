from django.test import TestCase

from .models import Word


class AnimalTestCase(TestCase):

    fixtures = ['words2000.json']

    def test_initial_words_count(self):
        count = Word.objects.all().count()
        self.assertEqual(count, 0)


