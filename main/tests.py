from __future__ import division

import random

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Word, Progress



class NoNameTestClass(TestCase):

    # called once per class
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('test', 'text@example.com', 'TestPassword123')


    fixtures = ['words-2000.json']




    def test_initial_words(self):
        # test of the test :)
        # initial fixture contains 2001 word
        count = Word.objects.all().count()
        self.assertEqual(count, 2001)




    def test_add_new_word(self):
        """
        Checking adding words to user's dict works properly
        """

        # adding one word to user's dict
        Progress.objects.addNewWord(self.user)

        count = Progress.objects.filter(user=self.user).count()
        self.assertEqual(count, 1)

        # checking that words been get in the right order (by rank)
        commonWord = Word.objects.all().order_by('rank')[0]
        userWord = Progress.objects.all()[0]
        self.assertEqual(commonWord.id, userWord.word_id)


        # adding 10 words to user's dict
        Progress.objects.addNewWordBulk(self.user, 10)

        count = Progress.objects.filter(user=self.user).count()
        self.assertEqual(count, 11)

        # completing user dict to 100 words
        Progress.objects.ensure100(self.user)
        count = Progress.objects.filter(user=self.user).count()
        self.assertEqual(count, 100)


        # checking that words been get in the right order
        commonWords = Word.objects.all().order_by('rank').values_list('id', flat=True)[1:100]
        userWord = Progress.objects.all().values_list('word_id', flat=True)[1:100]
        self.assertEqual(set(commonWords), set(userWord))






    def set_random_ratio(self, min, max):
        progress = Progress.objects.filter(user=self.user)
        for word in progress:
            word.ratio = random.randint(min, max)
            word.save()



    def test_get_avg_ratio(self):
        """
        Checking getAvgRatio works properly 
        test simple mode - 5 words
        """

        Progress.objects.addNewWordBulk(self.user, 5)

        progress = Progress.objects.filter(user=self.user)
        # making ration 0,1,2,3,4 so avg=2
        for key, word in enumerate(progress):
            word.ratio = key
            word.save()

        avg_ratio = Progress.objects.getAvgRatio(self.user)
        self.assertEqual(avg_ratio, 2)


        self.set_random_ratio(3,5)
        avg_ratio = Progress.objects.getAvgRatio(self.user)
        self.assertGreaterEqual(avg_ratio, 3)
        self.assertLessEqual(avg_ratio, 5)


        self.set_random_ratio(5,8)
        avg_ratio = Progress.objects.getAvgRatio(self.user)
        self.assertGreaterEqual(avg_ratio, 5)
        self.assertLessEqual(avg_ratio, 8)



    def test_get_avg_ratio_2(self):
        """
        Checking getAvgRatio works properly 
        test second mode - 300 words
        """

        Progress.objects.addNewWordBulk(self.user, 300)

        qs = Progress.objects.filter(user=self.user)

        # 200th border word
        border_word = qs[200]

        # make ratio of first 200 words 7
        qs.filter(id__lte=border_word.id).update(ratio=7)

        # make ratio of newest 100 words 3
        qs.filter(id__gt=border_word.id).update(ratio=3)

        # ensure that last 100 words doesn't affect on result
        avg_ratio = Progress.objects.getAvgRatio(self.user)
        self.assertLessEqual(avg_ratio, 7)




    def get_range_helper(self, count, iterations):
        results = {}
        for x in range(0, iterations):
            res =  Progress.objects.getRange(count)
            key = str(res[0]) + '_' + str(res[1])
            if not key in results:
                results[key] = 0
            results[key] += 1

        for key, value in results.iteritems():
            results[key] = {
                'count': value,
                'percent': value * 100 / iterations,
            }

        return results




    def test_get_range_1(self):
        """
        Testing helper function getRange()
        Test case 1
        if user's dict contains < 200
        Function must return None_None in 100% cases
        """
        word_count = 100
        iterations = 5000
        results = self.get_range_helper(word_count, iterations)
        self.assertIn('None_None', results)
        self.assertEqual(results['None_None']['percent'], 100)







    def get_range_2(self, word_count):
        iterations = 10000
        results = self.get_range_helper(word_count, iterations)
        self.assertIn('100_0', results)
        self.assertIn('None_100', results)
        
        self.assertGreater(results['100_0']['percent'], 48)
        self.assertLess(results['100_0']['percent'], 52)

        self.assertGreater(results['None_100']['percent'], 48)
        self.assertLess(results['None_100']['percent'], 52)



    def test_get_range_2(self):
        """
        Testing helper function getRange()
        Test case 2
        if user's dict contains >=300 and <650
        Function must return
        100_0 in 50% cases
        None_100 in 50% cases
        """
        self.get_range_2(300)
        self.get_range_2(500)
        self.get_range_2(649)





    def get_range_3(self, word_count):
        iterations = 10000
        results = self.get_range_helper(word_count, iterations)
        self.assertIn('100_0', results)
        self.assertIn('200_100', results)
        self.assertIn('None_200', results)
        
        self.assertGreater(results['100_0']['percent'], 48)
        self.assertLess(results['100_0']['percent'], 52)

        self.assertGreater(results['200_100']['percent'], 23)
        self.assertLess(results['200_100']['percent'], 27)

        self.assertGreater(results['None_200']['percent'], 23)
        self.assertLess(results['None_200']['percent'], 27)



    def test_get_range_3(self):
        """
        Testing helper function getRange()
        Test case 3
        if user's dict contains >=650 and <1000
        Function must return
        100_0 in 50% cases
        200_100 in 25% cases
        None_200 in 25% cases
        """
        self.get_range_3(650)
        self.get_range_3(800)
        self.get_range_3(999)




    def get_range_4(self, word_count):
        iterations = 10000
        results = self.get_range_helper(word_count, iterations)
        self.assertIn('100_0', results)
        self.assertIn('300_100', results)
        self.assertIn('None_300', results)
        
        self.assertGreater(results['100_0']['percent'], 48)
        self.assertLess(results['100_0']['percent'], 52)

        self.assertGreater(results['300_100']['percent'], 23)
        self.assertLess(results['300_100']['percent'], 27)

        self.assertGreater(results['None_300']['percent'], 23)
        self.assertLess(results['None_300']['percent'], 27)



    def test_get_range_4(self):
        """
        Testing helper function getRange()
        Test case 4
        if user's dict contains >= 1000
        Function must return
        100_0 in 50% cases
        300_100 in 25% cases
        None_300 in 25% cases
        """
        self.get_range_4(1000)
        self.get_range_4(2000)






