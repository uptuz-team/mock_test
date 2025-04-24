from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializer import *
from rest_framework.permissions import IsAuthenticated


# WritingTaskFirst API Views
class WritingTaskFirstList(APIView):
    def get(self, request, format=None):
        tasks = WritingTaskFirst.objects.all()
        serializer = WritingTaskFirstSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = WritingTaskFirstSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WritingTaskFirstDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            task = WritingTaskFirst.objects.get(pk=pk)
        except WritingTaskFirst.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WritingTaskFirstSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        try:
            task = WritingTaskFirst.objects.get(pk=pk)
        except WritingTaskFirst.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WritingTaskFirstSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            task = WritingTaskFirst.objects.get(pk=pk)
        except WritingTaskFirst.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# WritingTaskSecond API Views
class WritingTaskSecondList(APIView):
    def get(self, request, format=None):
        tasks = WritingTaskSecond.objects.all()
        serializer = WritingTaskSecondSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = WritingTaskSecondSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WritingTaskSecondDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            task = WritingTaskSecond.objects.get(pk=pk)
        except WritingTaskSecond.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WritingTaskSecondSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        try:
            task = WritingTaskSecond.objects.get(pk=pk)
        except WritingTaskSecond.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WritingTaskSecondSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            task = WritingTaskSecond.objects.get(pk=pk)
        except WritingTaskSecond.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WritingList(APIView):
    def get(self, request, format=None):
        writings = Writing.objects.all()
        serializer = WritingSerializer(writings, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = WritingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WritingDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            writing = Writing.objects.get(pk=pk)
        except Writing.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WritingSerializer(writing)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        try:
            writing = Writing.objects.get(pk=pk)
        except Writing.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = WritingSerializer(writing, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            writing = Writing.objects.get(pk=pk)
        except Writing.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        writing.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from rest_framework.exceptions import PermissionDenied
from .utils import check_writing_answer_with_ai, parse_ai_feedback


class WritingAnswerSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        writing_id = data.get("writing")
        task_number = int(data.get("task_number", 0))
        task_id = data.get("task_id")
        answer_text = data.get("answer_text")

        if not all([writing_id, task_number, task_id, answer_text]):
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            writing = Writing.objects.get(id=writing_id)
        except Writing.DoesNotExist:
            return Response({"error": "Writing not found."}, status=status.HTTP_404_NOT_FOUND)

        # Aniqlik bilan Taskni olib kelamiz
        if task_number == 1:
            from .models import WritingTaskFirst
            try:
                task = WritingTaskFirst.objects.get(id=task_id, writing=writing)
                writing_topic_or_data = task.title or task.text or "No task content."
            except WritingTaskFirst.DoesNotExist:
                return Response({"error": "Task 1 not found."}, status=status.HTTP_404_NOT_FOUND)
        elif task_number == 2:
            from .models import WritingTaskSecond
            try:
                task = WritingTaskSecond.objects.get(id=task_id, writing=writing)
                writing_topic_or_data = task.topic
            except WritingTaskSecond.DoesNotExist:
                return Response({"error": "Task 2 not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Invalid task number."}, status=status.HTTP_400_BAD_REQUEST)

        # AI tekshiruvi
        ai_raw = check_writing_answer_with_ai(answer_text, task_number, writing_topic_or_data)
        parsed = parse_ai_feedback(ai_raw)


        # ✅ Javob qaytarish

        return Response({
            "message": "Answer submitted successfully",
            "score": parsed["overall_band"],
            "feedback": parsed["overall_feedback"],
            "task_response": parsed["task_response"],
            "coherence_and_cohesion": parsed["coherence_and_cohesion"],
            "lexical_resource": parsed["lexical_resource"],
            "grammatical_range_and_accuracy": parsed["grammatical_range_and_accuracy"],
        }, status=status.HTTP_201_CREATED)

