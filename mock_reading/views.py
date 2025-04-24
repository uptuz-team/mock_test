from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.urls import path
from .models import IELTS, ReadingTest, Task, Question
from .serializers import *
import openai
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class IELTSAPIView(APIView):

    def get(self, request, pk=None):
        if pk:
            ielts = IELTS.objects.filter(pk=pk).first()
            if not ielts:
                return Response({'error': 'IELTS topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
            serializer = IELTSSerializer(ielts)
        else:
            ielts = IELTS.objects.all()
            serializer = IELTSSerializer(ielts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = IELTSSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReadingTestListCreateAPIView(generics.ListCreateAPIView):
    queryset = ReadingTest.objects.all()
    serializer_class = ReadingTestSerializer

# ReadingTest uchun GET (detail), PUT (update) va DELETE (delete)
class ReadingTestRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReadingTest.objects.all()
    serializer_class = ReadingTestSerializer



# **TASK API VIEWS**
class TaskListCreateAPIView(generics.ListCreateAPIView):
    """
    Task yaratish va barcha Task larni ko'rish uchun API.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Task ni detail ko'rish, o'zgartirish va o'chirish uchun API.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


# **QUESTION API VIEWS**
class QuestionListCreateAPIView(generics.ListCreateAPIView):
    """
    Barcha Question larni olish va yangi Question yaratish API.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Question ni detail ko'rish, o'zgartirish va o'chirish API.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]


# **Task bo‘yicha barcha savollarni olish uchun API**
class TaskQuestionsAPIView(APIView):
    """
    Berilgan Task ning barcha Question larini olish API.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        questions = task.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from .models import ReadingTest, Question, Answer, PupilReadingResult
from .serializers import AnswerCreateSerializer, AnswerResponseSerializer

class SubmitAnswersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AnswerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reading_test_id = serializer.validated_data['reading_test_id']
        answers_data = serializer.validated_data['answers']

        try:
            reading_test = ReadingTest.objects.get(id=reading_test_id)
        except ReadingTest.DoesNotExist:
            return Response({"error": "Reading test not found"}, status=status.HTTP_404_NOT_FOUND)

        pupil = request.user
        response_data = []
        answers_created = []

        for ans in answers_data:
            question_id = ans.get("question_id")
            answer_text = ans.get("answer_text")

            try:
                question = Question.objects.get(id=question_id, task__reading_test=reading_test)
            except Question.DoesNotExist:
                continue  # Skip invalid questions

            answer = Answer.objects.create(
                pupil=pupil,
                reading_test=reading_test,
                question=question,
                answer_text=answer_text
            )
            answers_created.append(answer)
            response_data.append(AnswerResponseSerializer(answer).data)

        # Calculate results
        correct_answers = sum(answer.is_correct for answer in answers_created)
        total_answered = len(answers_created)
        incorrect_answers = total_answered - correct_answers

        # Calculate total questions in the test
        total_questions = Question.objects.filter(task__reading_test=reading_test).count()

        # Calculate IELTS score (0.0 - 9.0)
        if total_questions == 0:
            score = 0.0
        else:
            score = (correct_answers / total_questions) * 9.0
        score = round(score, 1)  # Round to one decimal place

        # Save pupil's result
        PupilReadingResult.objects.create(
            pupil=pupil,
            reading_test=reading_test,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers,
            score=score,
            submitted_at=timezone.now()
        )

        return Response({
            "reading_test": reading_test.title,
            "total_questions_answered": total_answered,
            "correct_answers": correct_answers,
            "incorrect_answers": incorrect_answers,
            "ielts_score": score,
            "results": response_data
        }, status=status.HTTP_201_CREATED)































































# class ReadingTestAPIView(APIView):

    
#     def get(self, request, pk=None):
#         if pk:
#             reading_test = ReadingTest.objects.filter(pk=pk).first()
#             if not reading_test:
#                 return Response({'error': 'Reading test topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
#             serializer = ReadingTestSerializer(reading_test)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             reading_tests = ReadingTest.objects.all()
#             serializer = ReadingTestSerializer(reading_tests, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request, pk):
#         reading_test = ReadingTest.objects.filter(pk=pk).first()
#         if not reading_test:
#             return Response({'error': 'Reading test topilmadi!'}, status=status.HTTP_404_NOT_FOUND)

#         start_time = timezone.now()
#         request.session[f'reading_test_{pk}_start_time'] = start_time.isoformat()
#         return Response({'message': 'Reading test boshlandi', 'start_time': start_time}, status=status.HTTP_200_OK)

#     def put(self, request, pk):
#         start_time_str = request.session.get(f'reading_test_{pk}_start_time')
#         if not start_time_str:
#             return Response({'error': 'Test boshlanmagan!'}, status=status.HTTP_400_BAD_REQUEST)

#         start_time = timezone.datetime.fromisoformat(start_time_str)
#         elapsed_time = timezone.now() - start_time
#         if elapsed_time.total_seconds() > 3600:
#             return Response({'error': 'Vaqt tugagan!'}, status=status.HTTP_400_BAD_REQUEST)
        
#         return Response({'message': 'Javob qabul qilindi!'}, status=status.HTTP_200_OK)





# # views.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from django.utils import timezone

# class StartTestAPI(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, test_id):
#         test = get_object_or_404(ReadingTest, id=test_id)
#         result = TestResult.objects.create(
#             user=request.user,
#             reading_test=test,
#             started_at=timezone.now()
#         )
#         return Response({'test_id': test.id, 'result_id': result.id})



# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.utils import timezone

# class SubmitAnswerAPIView(APIView):
    
#     def post(self, request, test_id):
#         start_time_str = request.session.get(f'reading_test_{test_id}_start_time')
#         if not start_time_str:
#             return Response({'error': 'Test boshlanmagan!'}, status=status.HTTP_400_BAD_REQUEST)

#         start_time = timezone.datetime.fromisoformat(start_time_str)
#         if (timezone.now() - start_time).total_seconds() > 3600:
#             return Response({'error': 'Vaqt tugagan!'}, status=status.HTTP_400_BAD_REQUEST)

#         serializer = AnswerSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Javob saqlandi', 'data': serializer.data}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def get(self, request, result_id):
#         try:
#             # result_id orqali natijani olish
#             result = Answer.objects.get(id=result_id)
#             # Javob qaytarish
#             return Response({
#                 'id': result.id,
#                 'answer_text': result.answer_text,
#                 'is_correct': result.is_correct
#             }, status=status.HTTP_200_OK)
#         except Answer.DoesNotExist:
#             return Response({'error': 'Answer not found'}, status=status.HTTP_404_NOT_FOUND)


# from django.shortcuts import get_object_or_404
# from rest_framework import viewsets
# from rest_framework.response import Response
# from .models import TestResult
# from .serializers import TestResultSerializer
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import action  # import action here

# class TestResultViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]

#     def retrieve(self, request, result_id=None):
#         """Foydalanuvchining o'z test natijasini ID orqali olish"""
#         test_result = get_object_or_404(TestResult, id=result_id, user=request.user)
#         serializer = TestResultSerializer(test_result)
#         return Response(serializer.data)

#     def list(self, request):
#         """Foydalanuvchining o'z barcha test natijalarini olish"""
#         # faqat login qilgan foydalanuvchining test natijalari
#         test_results = TestResult.objects.filter(user=request.user)
#         serializer = TestResultSerializer(test_results, many=True)
#         return Response(serializer.data)

#     @action(detail=True, methods=['post'])
#     def submit_test(self, request, pk=None):
#         """Foydalanuvchining test natijasini saqlash"""
#         user = request.user  # Hozirgi login qilgan foydalanuvchi
#         score = request.data.get('score')
#         total_questions = request.data.get('total_questions')
#         correct_answers = request.data.get('correct_answers')

#         # Test natijasini yaratish
#         test_result = TestResult.objects.create(
#             user=user,
#             score=score,
#             total_questions=total_questions,
#             correct_answers=correct_answers
#         )

#         return Response({
#             "message": "Test natijasi muvaffaqiyatli saqlandi.",
#             "test_result": TestResultSerializer(test_result).data
#         })


# class AnswerViewSet(viewsets.ModelViewSet):
#     queryset = Answer.objects.all()
#     serializer_class = AnswerSerializer


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.authtoken.models import Token
# from django.utils import timezone
# from django.contrib.auth import get_user_model, authenticate
# from .models import Question, Answer
# from .serializers import AnswerSerializer
# import openai
# from django.conf import settings

# User = get_user_model()

# class SubmitAnswersAPIView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         answers_data = request.data.get('answers', [])
        
#         if not answers_data:
#             return Response({'error': 'Javoblar kiritilmagan!'}, status=status.HTTP_400_BAD_REQUEST)

#         question_ids = [a.get('question') for a in answers_data]
#         questions = {q.id: q for q in Question.objects.filter(id__in=question_ids).select_related('task__reading_test')}

#         reading_test = next(iter(questions.values())).task.reading_test

#         start_time_str = request.session.get(f'reading_test_{reading_test.id}_start_time')
#         if not start_time_str:
#             return Response({'error': 'Test boshlanmagan!'}, status=status.HTTP_400_BAD_REQUEST)

#         start_time = timezone.datetime.fromisoformat(start_time_str)
#         if (timezone.now() - start_time).total_seconds() > reading_test.allowed_time * 60:
#             return Response({'error': 'Vaqt tugadi!'}, status=status.HTTP_400_BAD_REQUEST)

#         serializer = AnswerSerializer(data=answers_data, many=True, context={'request': request})
#         if serializer.is_valid():
#             answers = serializer.save(user=request.user)
#             return Response({'message': 'Javoblar saqlandi', 'answers': AnswerSerializer(answers, many=True).data}, status=201)
        
#         return Response(serializer.errors, status=400)

#     def check_with_chatgpt(self, answers):
#         openai.api_key = settings.OPENAI_API_KEY  # API kalit xavfsiz
#         batch_size = 2  # Batch hajmi
        
#         for i in range(0, len(answers), batch_size):
#             batch = answers[i:i + batch_size]
#             prompt = "Quyidagi javoblarni tekshiring. Har bir javob uchun 'correct' yoki 'incorrect' deb javob bering:\n\n"
            
#             for idx, answer in enumerate(batch, 1):
#                 prompt += f"{idx}. Savol: {answer.question.question_text}\nTo'g'ri javob: {answer.question.correct_answer}\nFoydalanuvchi javobi: {answer.answer_text}\n\n"

#             try:
#                 response = openai.ChatCompletion.create(
#                     model="gpt-4-turbo",
#                     messages=[{"role": "user", "content": prompt}],
#                     temperature=0,
#                     max_tokens=500
#                 )
#                 self.parse_gpt_response(response.choices[0].message['content'], batch)
#             except Exception as e:
#                 print(f"Xatolik: {e}")

#     def parse_gpt_response(self, response_text, batch):
#         lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        
#         for idx, line in enumerate(lines):
#             if idx >= len(batch):
#                 break
            
#             parts = line.split(':', 1)
#             if len(parts) < 2:
#                 continue
            
#             correctness, feedback = parts[0].lower(), parts[1].strip()
#             answer = batch[idx]
#             answer.is_correct = correctness.startswith('correct')
#             answer.feedback = feedback
#             answer.save()















# class StartExamAPI(APIView):
#     def post(self, request):
#         user = request.user
#         if user.role != 'pupil':
#             return Response({"error": "Faqat o'quvchi imtihon topshira oladi"}, status=403)
        
#         reading_test_id = request.data.get('reading_test_id')
#         try:
#             reading_test = ReadingTest.objects.get(id=reading_test_id)
#         except ReadingTest.DoesNotExist:
#             return Response({"error": "Test topilmadi"}, status=404)
        
#         # Faqat 1 ta aktiv sessiya
#         if ExamSession.objects.filter(user=user, is_active=True).exists():
#             return Response({"error": "Sizda aktiv imtihon mavjud"}, status=400)
        
#         exam_session = ExamSession.objects.create(
#             user=user,
#             reading_test=reading_test
#         )
#         return Response({
#             "message": "Imtihon boshlandi!",
#             "end_time": exam_session.end_time
#         }, status=201)

# class SubmitAnswerAPI(APIView):
#     def post(self, request):
#         user = request.user
#         exam_session = ExamSession.objects.filter(user=user, is_active=True).first()
        
#         # Vaqt tekshirish
#         if not exam_session or timezone.now() > exam_session.end_time:
#             exam_session.is_active = False
#             exam_session.save()
#             return Response({"error": "Imtihon vaqti tugagan"}, status=400)
        
#         question_id = request.data.get('question_id')
#         user_answer = request.data.get('answer')
        
#         try:
#             question = Question.objects.get(id=question_id)
#         except Question.DoesNotExist:
#             return Response({"error": "Savol topilmadi"}, status=404)
        
#         # ChatGPTga jo'natish
#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-4",
#                 messages=[
#                     {"role": "system", "content": "Siz IELTS instruktorsiz. Foydalanuvchi javobini tekshiring."},
#                     {"role": "user", "content": f"""
#                     Passage: {question.task.content}
#                     Savol: {question.text}
#                     Foydalanuvchi javobi: {user_answer}
#                     To'g'ri javob: {question.correct_answer}
#                     Ushbu javob to'g'rimi?
#                     """}
#                 ]
#             )
#             ai_response = response.choices[0].message['content']
#             is_correct = "ha" in ai_response.lower()  # ChatGPT javobiga qarab o'zgartirish
#         except Exception as e:
#             ai_response = str(e)
#             is_correct = False
        
#         # Javobni saqlash
#         Answer.objects.create(
#             exam_session=exam_session,
#             question=question,
#             user_answer=user_answer,
#             is_correct=is_correct,
#             ai_feedback=ai_response
#         )
        
#         return Response({"message": "Javob qabul qilindi", "ai_feedback": ai_response})
    
    
    