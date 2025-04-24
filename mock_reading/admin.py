from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import IELTS, ReadingTest, Task, Question, Answer

admin.site.register(Answer)

# IELTS model admin configuration
@admin.register(IELTS)
class IELTSAdmin(admin.ModelAdmin):
    list_display = ('user', "title", 'created_at', 'updated_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)

# Formset to limit the number of tasks to 3 for each ReadingTest
class TaskInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super().clean()
        # Count the number of tasks (excluding deleted ones)
        count = sum(1 for form in self.forms if not form.cleaned_data.get('DELETE', False))
        if count > 3:
            raise ValidationError("Har bir Reading Testda maksimum 3 ta Task bo'lishi mumkin!")

# Inline admin for Task in ReadingTest
class TaskInline(admin.TabularInline):
    model = Task
    formset = TaskInlineFormset
    extra = 1
    max_num = 3
    fields = ('title', 'pdf_for_task', 'img')  # Removed 'question_text' from here
    verbose_name = 'Vazifa'
    verbose_name_plural = 'Vazifalar'

# ReadingTest model admin configuration
@admin.register(ReadingTest)
class ReadingTestAdmin(admin.ModelAdmin):
    inlines = [TaskInline]
    list_display = ('title', 'created_at', 'updated_at', 'tasks_count')
    search_fields = ('title',)
    list_filter = ('created_at',)
    
    def tasks_count(self, obj):
        return obj.tasks.count()
    tasks_count.short_description = 'Vazifalar soni'

# Inline admin for Question in Task
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('question_text', 'question_type', 'enter_word', 'True_False', 'a', 'b', 'c', 'd', 'correct_test_ansver')  # Updated fields for Question
    verbose_name = 'Savol'
    verbose_name_plural = 'Savollar'

# Task model admin configuration
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'reading_test', 'created_at', 'questions_count')
    list_filter = ('reading_test', 'created_at')
    search_fields = ('title', 'reading_test__title')
    
    def questions_count(self, obj):
        return obj.questions.count()
    questions_count.short_description = 'Savollar soni'

# Question model admin configuration
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id','truncated_question', 'task', 'question_type', 'created_at')
    list_filter = ('question_type', 'task__reading_test')
    search_fields = ('question_text', 'task__title')
    
    def truncated_question(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    truncated_question.short_description = 'Savol matni'
