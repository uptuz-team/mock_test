from rest_framework import serializers
from .models import *
from .utils import  *


class WritingTaskFirstSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingTaskFirst
        fields = "__all__"  # Barcha maydonlarni olish


class WritingTaskSecondSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingTaskSecond
        fields = "__all__"  # Barcha maydonlarni olish


class WritingSerializer(serializers.ModelSerializer):
    task_firsts = WritingTaskFirstSerializer(many=True, read_only=True)
    task_seconds = WritingTaskSecondSerializer(many=True, read_only=True)

    class Meta:
        model = Writing
        fields = ["ielts", "title", "allow_time", "create_at", "update_at", "task_firsts", "task_seconds"]



class WritingAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = WritingAnswer
        fields = ['writing', 'user', 'task_number', 'answer_text', 'score', 'feedback', 'checked_by_ai', 'submitted_at']
        read_only_fields = ['score', 'feedback', 'checked_by_ai', 'submitted_at', 'user']
