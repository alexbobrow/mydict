import random

import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory

from main.models import Word, Progress


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user-{n}@example.org')
    username = factory.Sequence(lambda n: f'User {n}')
    password = factory.PostGenerationMethodCall('set_password', 'default')


class WordFactory(DjangoModelFactory):
    class Meta:
        model = Word

    word = factory.Sequence(lambda n: f'word{n}')
    translation = factory.Sequence(lambda n: f'translation{n}')
    frequency = factory.LazyFunction(lambda: random.randrange(0, 10000))
    rank = factory.LazyFunction(lambda: random.randrange(0, 10000))
    pronounce = factory.Sequence(lambda n: f'path/to/file{n}.mp3')


class ProgressFactory(DjangoModelFactory):
    class Meta:
        model = Progress

    word = factory.SubFactory(WordFactory)
    user = factory.SubFactory(UserFactory)

    know_count = factory.LazyFunction(lambda: random.randrange(1, 5))
    know_first = factory.LazyFunction(lambda: random.randrange(1, 5))
    know_avg = factory.LazyFunction(lambda: random.randrange(1, 5))
    know_last = factory.LazyFunction(lambda: random.randrange(1, 5))
