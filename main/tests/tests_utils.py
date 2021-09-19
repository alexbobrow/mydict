from django.test import TestCase

from main.tests.factories import UserFactory, WordFactory, ProgressFactory
from main.utils import get_next_word


class TestGetNextWord(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_without_progress_no_filters(self):
        WordFactory.create_batch(10)
        get_next_word(self.user, '')

    def test_only_progress_no_filters(self):
        ProgressFactory.create_batch(10, user=self.user)
        get_next_word(self.user, '')

    def test_mixed_no_filters(self):
        words_ids_with_progress = [progress.word_id for progress in ProgressFactory.create_batch(3, user=self.user)]
        words_ids_without_progress = [word.id for word in WordFactory.create_batch(3)]
        selected_words_ids = []
        for x in range(10):
            word = get_next_word(self.user, '')
            selected_words_ids.append(word.id)
        # Ensure we select both type of words
        self.assertTrue(set(words_ids_with_progress) & set(selected_words_ids))
        self.assertTrue(set(words_ids_without_progress) & set(selected_words_ids))

    def test_only_new(self):
        words_ids_with_progress = [progress.word_id for progress in ProgressFactory.create_batch(3, user=self.user)]
        words_ids_without_progress = [word.id for word in WordFactory.create_batch(3)]
        selected_words_ids = []
        for x in range(10):
            word = get_next_word(self.user, '0')
            selected_words_ids.append(word.id)
        # Ensure we select only new
        self.assertFalse(set(words_ids_with_progress) & set(selected_words_ids))
        self.assertTrue(set(words_ids_without_progress) & set(selected_words_ids))

    def test_only_with_progress(self):
        words_ids_with_progress = [progress.word_id for progress in ProgressFactory.create_batch(3, user=self.user)]
        words_ids_without_progress = [word.id for word in WordFactory.create_batch(3)]
        selected_words_ids = []
        for x in range(10):
            word = get_next_word(self.user, '12345')
            selected_words_ids.append(word.id)
        # Ensure we select only new
        self.assertTrue(set(words_ids_with_progress) & set(selected_words_ids))
        self.assertFalse(set(words_ids_without_progress) & set(selected_words_ids))

    def test_only_with_progress_3(self):
        ProgressFactory(user=self.user, know_last=1)
        ProgressFactory(user=self.user, know_last=2)
        ProgressFactory(user=self.user, know_last=4)
        ProgressFactory(user=self.user, know_last=5)
        progress_3 = ProgressFactory(user=self.user, know_last=3)
        WordFactory.create_batch(3)
        for x in range(10):
            # Same word always selected since it is the only word with progress 3
            word = get_next_word(self.user, '3')
            self.assertEqual(progress_3.word, word)
