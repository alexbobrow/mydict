from django.test import TestCase
from django.urls import reverse

from main.models import Progress, Word, Report
from main.tests.consts import ERROR_NO_WORDS
from main.tests.factories import UserFactory, WordFactory, ProgressFactory


class TestViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'about.html')

    def test_cards(self):
        url = reverse('cards')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'cards.html')

    def test_list_success(self):
        self.client.force_login(self.user)
        url = reverse('list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_list_access_denied(self):
        url = reverse('list')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_stata_not_staff(self):
        url = reverse('stata')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_stata_staff(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)
        url = reverse('stata')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'stata.html')


class TestApiViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def setUp(self):
        self.user.refresh_from_db()

    def test_next_as_guest_no_words(self):
        url = reverse('next')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertJSONEqual(response.content, {
            "error": ERROR_NO_WORDS
        })

    def test_next_as_guest(self):
        word = WordFactory()
        url = reverse('next')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertJSONEqual(response.content, {
            "en": word.word,
            "ru": word.translation,
            "pronounce": word.pronounce.url,
            "wordId": word.id,
        })

    def test_next_as_user_several_words(self):
        self.client.force_login(self.user)

        ProgressFactory.create_batch(5, user=self.user, know_last=5)
        ProgressFactory.create_batch(4, user=self.user, know_last=4)
        ProgressFactory.create_batch(3, user=self.user, know_last=3)
        ProgressFactory.create_batch(2, user=self.user, know_last=2)
        ProgressFactory.create_batch(1, user=self.user, know_last=1)

        WordFactory.create_batch(6)

        url = reverse('next')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        word_id = response.json()['wordId']
        word = Word.objects.get(id=word_id)
        progress = Progress.objects.get(word=word, user=self.user)

        self.assertJSONEqual(response.content, {
            "knowLast": progress.know_last,
            "newTotal": 6,
            "progress1": 1,
            "progress2": 2,
            "progress3": 3,
            "progress4": 4,
            "progress5": 5,
            "progressId": progress.id,
            "total": 21,
            "en": word.word,
            "ru": word.translation,
            "pronounce": word.pronounce.url,
            "wordId": word.id,
        })

    def test_next_as_user_with_filter(self):
        self.client.force_login(self.user)
        progress_5 = ProgressFactory(user=self.user, know_last=5)
        progress_4 = ProgressFactory(user=self.user, know_last=4)
        progress_3 = ProgressFactory(user=self.user, know_last=3)
        progress_2 = ProgressFactory(user=self.user, know_last=2)
        progress_1 = ProgressFactory(user=self.user, know_last=1)
        url = reverse('next')

        response = self.client.post(url, dict(filters='1'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(progress_1.word.id, response.json()['wordId'])

        response = self.client.post(url, dict(filters='2'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(progress_2.word.id, response.json()['wordId'])

        response = self.client.post(url, dict(filters='3'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(progress_3.word.id, response.json()['wordId'])

        response = self.client.post(url, dict(filters='4'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(progress_4.word.id, response.json()['wordId'])

        response = self.client.post(url, dict(filters='5'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(progress_5.word.id, response.json()['wordId'])

    def test_apply_progress_new(self):
        self.client.force_login(self.user)
        progress = ProgressFactory(user=self.user, know_count=0, know_first=0, know_avg=0, know_last=0)
        url = reverse('next')
        data = {
            'answer_value': 3,
            'progress_id': progress.id,
            'filters': 54321
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        progress.refresh_from_db()
        self.assertEqual(3, progress.know_last)
        self.assertEqual(3, progress.know_avg)
        self.assertEqual(1, progress.know_count)

    def test_apply_progress_existing(self):
        self.client.force_login(self.user)
        progress = ProgressFactory(user=self.user, know_count=2, know_first=2, know_avg=2, know_last=2)
        url = reverse('next')
        data = {
            'answer_value': 5,
            'progress_id': progress.id,
            'filters': 54321
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        progress.refresh_from_db()
        self.assertEqual(5, progress.know_last)
        self.assertEqual(3, progress.know_avg)
        self.assertEqual(3, progress.know_count)

    def test_report_word(self):
        self.client.force_login(self.user)
        word = WordFactory()
        url = reverse('report')
        data = {
            'word_id': word.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        self.assertJSONEqual(response.content, dict(success=True))
        self.assertTrue(Report.objects.filter(user=self.user, word=word).exists())

    def test_delete_word_not_staff(self):
        self.client.force_login(self.user)
        word = WordFactory()
        self.assertFalse(word.disabled)
        url = reverse('delete')
        data = {
            'word_id': word.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(403, response.status_code)
        word.refresh_from_db()
        self.assertFalse(word.disabled)

    def test_delete_word_staff(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)
        word = WordFactory()
        self.assertFalse(word.disabled)
        url = reverse('delete')
        data = {
            'word_id': word.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        self.assertJSONEqual(response.content, dict(success=True))
        word.refresh_from_db()
        self.assertTrue(word.disabled)

    def test_update_word_not_staff(self):
        self.client.force_login(self.user)
        word = WordFactory(translation="version1")
        url = reverse('admin_update')
        data = {
            'word_id': word.id,
            'translation': 'version2'
        }
        response = self.client.post(url, data)
        self.assertEqual(403, response.status_code)
        word.refresh_from_db()
        self.assertEqual('version1', word.translation)

    def test_update_word_staff(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)
        word = WordFactory(translation="version1")
        url = reverse('admin_update')
        data = {
            'word_id': word.id,
            'translation': 'version2'
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        word.refresh_from_db()
        self.assertEqual('version1', word.old_translation)
        self.assertEqual('version2', word.translation)
