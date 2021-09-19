from rest_framework import serializers

from main.models import Preferences, Word, Progress


class WordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Word
        fields = ('id', 'en', 'ru', 'pronounce')
        extra_kwargs = {
            'en': {'source': 'word'},
            'ru': {'source': 'translation'},
        }


class ProgressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Progress
        fields = ('knowLast',)
        extra_kwargs = {
            'knowLast': {'source': 'know_last'},
        }


class PreferencesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Preferences
        fields = ('show_sidebar', 'filters', 'answer_delay')
        extra_kwargs = {'filters': {'allow_blank': True}}
