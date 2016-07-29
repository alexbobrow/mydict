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
            word.ratio = random.randint(min*10, max*10)/10
            word.save()



    def test_get_avg_ratio(self):
        """
        Checking getAvgRatio works properly 
        test simple mode - 5 words
        """

        Progress.objects.addNewWordBulk(self.user, 5)

        progress = Progress.objects.filter(user=self.user)
        # making ration 0, .1, .2, .3, .4 so avg=.2
        for key, word in enumerate(progress):
            word.ratio = key / 10
            word.save()

        avg_ratio = Progress.objects.getAvgRatio(self.user)
        self.assertEqual(avg_ratio, 0.2)


        self.set_random_ratio(0.3, 0.5)
        avg_ratio = Progress.objects.getAvgRatio(self.user)
        self.assertGreaterEqual(avg_ratio, 0.3)
        self.assertLessEqual(avg_ratio, 0.5)


        self.set_random_ratio(0.5, 0.8)
        avg_ratio = Progress.objects.getAvgRatio(self.user)
        self.assertGreaterEqual(avg_ratio, 0.5)
        self.assertLessEqual(avg_ratio, 0.8)



    def test_get_avg_ratio_2(self):
        """
        Checking getAvgRatio works properly 
        test second mode - 300 words
        """

        Progress.objects.addNewWordBulk(self.user, 300)

        qs = Progress.objects.filter(user=self.user)

        # 200th border word
        border_word = qs[200]

        # make ratio of first 200 words .7
        qs.filter(id__lte=border_word.id).update(ratio=0.7)

        # make ratio of newest 100 words .3
        qs.filter(id__gt=border_word.id).update(ratio=0.3)

        # ensure that last 100 words doesn't affect on result
        avg_ratio = Progress.objects.getAvgRatio(self.user)
        self.assertLessEqual(avg_ratio, 0.7)




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
        self.assertIn('0_100', results)
        self.assertIn('100_None', results)
        
        self.assertGreater(results['0_100']['percent'], 48)
        self.assertLess(results['0_100']['percent'], 52)

        self.assertGreater(results['100_None']['percent'], 48)
        self.assertLess(results['100_None']['percent'], 52)



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
        self.assertIn('0_100', results)
        self.assertIn('100_200', results)
        self.assertIn('200_None', results)
        
        self.assertGreater(results['0_100']['percent'], 48)
        self.assertLess(results['0_100']['percent'], 52)

        self.assertGreater(results['100_200']['percent'], 23)
        self.assertLess(results['100_200']['percent'], 27)

        self.assertGreater(results['200_None']['percent'], 23)
        self.assertLess(results['200_None']['percent'], 27)



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
        self.assertIn('0_100', results)
        self.assertIn('100_300', results)
        self.assertIn('300_None', results)
        
        self.assertGreater(results['0_100']['percent'], 48)
        self.assertLess(results['0_100']['percent'], 52)

        self.assertGreater(results['100_300']['percent'], 23)
        self.assertLess(results['100_300']['percent'], 27)

        self.assertGreater(results['300_None']['percent'], 23)
        self.assertLess(results['300_None']['percent'], 27)



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


    
    def test_get_next_1(self):
        """
        Ensuring that getNext() decide create word
        or use old one for repeat in the right way
        """

        # adding first 100 words
        Progress.objects.ensure100(self.user)

        qs = Progress.objects.filter(user=self.user)
        
        # mark words as showed
        qs.update(show_count=1)

        # function must return old words in 100% cases
        # because ratio=0
        for x in range(0, 100):
            # must be an old word
            progress_word = Progress.objects.getNext(self.user)
            self.assertEqual(progress_word.show_count, 1)


        # additional check that no new words added
        self.assertEqual(qs.count(), 100)


        # function must return new words in 100% cases
        # because ratio=1
        qs.update(ratio=1, show_count=1)
        for x in range(0, 100):
            # must be a new word
            progress_word = Progress.objects.getNext(self.user)
            self.assertEqual(progress_word.show_count, 0)

            progress_word.ratio=1
            progress_word.show_count=1
            progress_word.save()



        # additional check that 100 new words added
        self.assertEqual(qs.count(), 200)



        # function must return new words in 50% cases, and old in 50%
        # because ratio=0.75
        new = 0
        old = 0

        iterations = 500

        qs.update(ratio=0.75, show_count=1)

        for x in range(0, iterations):
            # can be new or old word as well
            progress_word = Progress.objects.getNext(self.user)
            if progress_word.show_count == 1:
                old += 1
            else:
                new += 1

            if progress_word.show_count != 1:
                progress_word.ratio=0.75
                progress_word.show_count=1
                progress_word.save()


        new_perc = new * 100 / iterations
        self.assertGreater(new_perc, 45)
        self.assertLess(new_perc, 55)




    def test_get_next_2(self):
        """
        Ensuring that getNext() pick word
        form the correct range
        """

        Progress.objects.addNewWordBulk(self.user, 100)

        for x in range(1200):


            progress_word = Progress.objects.getNext(self.user)

            # getting processed ranges from debug info
            range_start = progress_word.debug['range_start']
            range_end = progress_word.debug['range_end']

            # getting only ids
            qs = Progress.objects.filter(user=self.user).order_by('-id').values('id')
            
            # imitating same range
            if range_end is not None:
                qs = qs[range_start:range_end]
            else:
                # not sure if it will work with mysql, because it
                # is not support OFFSET without LIMIT
                qs = qs[range_start:]

            # checking the word is present in this range
            qs2 = Progress.objects.filter(id__in=qs).filter(id=progress_word.id)
            
            self.assertEqual(qs2.exists(), True)

            # increasing user's dict for one word
            Progress.objects.addNewWord(self.user)














