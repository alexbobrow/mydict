from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from main.exceptions import NextWordNotFound
from main.models import Progress, Word, Report, Preferences
from main.serializers import PreferencesSerializer
from main.tests.consts import ERROR_NO_WORDS


class NextView(APIView):

    def post(self, request):
        if request.user.is_authenticated:
            if 'progress_id' in request.POST:
                # fixating answer
                progress = Progress.objects.get(pk=request.POST['progress_id'])
                progress.add_answer(request.POST['answer_value'])

        filters = request.POST.get('filters', '')

        try:
            res, stata, debug = Progress.objects.get_next(request.user, filters)
        except NextWordNotFound:
            return Response({
                'error': ERROR_NO_WORDS
            })

        if request.user.is_authenticated:
            context = stata
            progress = res
            word = progress.word
            context['progressId'] = progress.id
            context['knowLast'] = progress.know_last
        else:
            context = {}
            progress = None
            word = res

        context['wordId'] = word.id
        context['en'] = word.word
        context['ru'] = word.translation
        context['pronounce'] = word.pronounce.url

        if request.user.is_staff:
            context['debug'] = debug

        return Response(context)


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
