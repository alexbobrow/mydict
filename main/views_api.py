from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from main.exceptions import NextWordNotFound
from main.models import Progress, Word, Report, Preferences
from main.serializers import PreferencesSerializer, WordSerializer, ProgressSerializer
from main.tests.consts import ERROR_NO_WORDS
from main.utils import get_next_word, get_progress_stats


class NextView(APIView):

    def post(self, request):

        if request.user.is_authenticated and 'progress_id' in request.POST:
            progress = Progress.objects.get(pk=request.POST['progress_id'])
            progress.add_answer(request.POST['answer_value'])

        filters = request.POST.get('filters', '')

        try:
            word = get_next_word(request.user, filters)
        except NextWordNotFound:
            return Response({
                'error': ERROR_NO_WORDS
            })

        response_data = {
            'word': WordSerializer(instance=word).data
        }

        if not request.user.is_authenticated:
            return Response(response_data)

        progress = Progress.objects.filter(user=request.user, word=word).first()
        if progress:
            response_data['progress'] = ProgressSerializer(instance=progress).data

        response_data['stats'] = get_progress_stats(request.user)

        return Response(response_data)


class ReportWordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        word = Word.objects.get(pk=request.POST['word_id'])
        Report.objects.create(
            user=request.user,
            word=word,
        )
        return Response({
            'success': True
        })


class DeleteWordView(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request):
        word = Word.objects.get(pk=request.POST['word_id'])
        word.disabled = True
        word.save()

        return Response({
            'success': True
        })


class UpdateWordView(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request):
        word = Word.objects.get(pk=request.POST['word_id'])
        word.old_translation = word.translation
        word.translation = request.POST['translation']
        word.save()

        return Response({
            'success': True
        })


class PreferenceUpdateView(UpdateModelMixin, GenericAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = PreferencesSerializer

    def get_object(self):
        preferences, _ = Preferences.objects.get_or_create(user=self.request.user)
        return preferences

    def put(self, request):
        return self.update(request)

    def patch(self, request):
        return self.partial_update(request)
