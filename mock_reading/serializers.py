from rest_framework import serializers
from .models import IELTS, ReadingTest, Task, Question
from .models import Answer


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

    
# serializers.py da AnswerSerializer qo'shamiz

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'answer_text', 'is_correct', 'feedback', 'created_at']
        read_only_fields = ['user', 'is_correct', 'feedback', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)  
    
    class Meta:
        model = Task
        fields = ["id", "reading_test", "title", "pdf_for_task", "img", "questions", "created_at", "updated_at"]


class ReadingTestSerializer(serializers.ModelSerializer):
    
    tasks = TaskSerializer(many=True, read_only=True)  
    
    class Meta:
        model = ReadingTest
        fields = ["id", "title", "allowed_time", "tasks", "created_at", "updated_at"]


class IELTSSerializer(serializers.ModelSerializer):
    reading_obj = ReadingTestSerializer(many=True, read_only=True, source = 'readingtest_set')  
    
    class Meta:
        model = IELTS
        fields = ["id", "user","title", "reading_obj", "created_at", "updated_at"]




class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'pupil', 'reading_test', 'question', 'answer_text', 'is_correct']

    def validate_answer_text(self, value):
        # Check if the answer is valid for the given question
        if not value.strip():
            raise serializers.ValidationError("Answer cannot be empty.")
        return value






class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'pupil', 'reading_test', 'question', 'answer_text', 'is_correct']

    def validate_answer_text(self, value):
        # Ensure the answer is not empty
        if not value.strip():
            raise serializers.ValidationError("Answer cannot be empty.")
        return value


from rest_framework import serializers
from .models import Answer, Question, ReadingTest


class AnswerCreateSerializer(serializers.Serializer):
    reading_test_id = serializers.IntegerField()
    answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    
    def validate(self, data):
        reading_test_id = data['reading_test_id']
        try:
            ReadingTest.objects.get(id=reading_test_id)
        except ReadingTest.DoesNotExist:
            raise serializers.ValidationError("Bunday ReadingTest mavjud emas.")
        return data


class AnswerResponseSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source='question.id')
    question_text = serializers.CharField(source='question.question_text')
    question_type = serializers.CharField(source='question.question_type')

    class Meta:
        model = Answer
        fields = ['question_id', 'question_text', 'question_type', 'answer_text', 'is_correct']






# # serializers.py
# from rest_framework import serializers
# from .models import *

# class QuestionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Question
#         fields = ['id', 'question_type', 'question_text', 'enter_word', 
#                  'True_or_False', 'a', 'b', 'c', 'd']

# class AnswerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Answer
#         fields = ['id', 'user', 'question', 'answer_text', 'is_correct', 'created_at', 'updated_at']

# class TestResultSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TestResult
#         fields = ['id', 'score', 'total_questions', 'correct_answers', 'created_at']
