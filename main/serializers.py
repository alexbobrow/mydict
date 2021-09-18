from rest_framework import serializers

from main.models import Preferences


class PreferencesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Preferences
        fields = ('show_sidebar', 'filters', 'answer_delay')
