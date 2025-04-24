from django.db import models
from author.models import User
from django.utils import timezone
from django.db import models
from django.utils import timezone


class IELTS(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length = 100,  null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - IELTS"
    
    class Meta:
        verbose_name = "IELTS"
        verbose_name_plural = "IELTS"
        ordering = ['-created_at']
        

class ReadingTest(models.Model):
    title = models.CharField(max_length=255)
    IELTS = models.ForeignKey(IELTS, null=True, blank=True,  on_delete=models.CASCADE)
    allowed_time = models.PositiveIntegerField(default=60, help_text="Vaqt daqiqada")   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_tasks(self):
        """Ushbu testga tegishli barcha Task obyektlarini qaytaradi."""
        return self.tasks.all()



class Task(models.Model):
    reading_test = models.ForeignKey(ReadingTest, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    pdf_for_task = models.FileField(upload_to='task_pdfs/', null=True, blank=True)
    img = models.ImageField(upload_to='task_images/', null=True, blank=True)
    task_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title

    def get_questions(self):
        """Ushbu Task ga tegishli barcha Question obyektlarini qaytaradi."""
        return self.questions.all()


from django.core.exceptions import ValidationError

class Question(models.Model):
    task = models.ForeignKey(Task, related_name='questions', on_delete=models.CASCADE)

    QUESTION_TYPES = (
        ("so'z keritish", "so'z keritish"),
        ('tf', 'True/False'),
        ("test", "test"),
    )
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        default='',
        verbose_name="Savol turi"
    )

    question_text = models.TextField(blank=True, null=True)
    enter_word = models.CharField(max_length=100, verbose_name="suzni kerililadi", blank=True, null=True)

    TRUE_OR_FALSE_CHOICES = (
        ("True", "True"),
        ('False', 'False'),
        ("Not given", "Not given"),
    )
    true_or_false = models.CharField(max_length=20, choices=TRUE_OR_FALSE_CHOICES, blank=True, null=True)

    a = models.CharField(max_length=200, null=True, blank=True)
    b = models.CharField(max_length=200, null=True, blank=True)
    c = models.CharField(max_length=200, null=True, blank=True)
    d = models.CharField(max_length=200, null=True, blank=True)
    test_answer_choices = (
        ("a", "a"),
        ('b', 'b'),
        ("c", "c"),
        ("d", "d"),
    )
    correct_test_answer = models.CharField(choices=test_answer_choices, max_length=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


class Answer(models.Model):
    pupil = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'pupil'},
        null=True,
        blank=True
    )
    reading_test = models.ForeignKey(ReadingTest, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pupil.username} - {self.question.id} - {self.answer_text}"

    def check_correctness(self):
        correct = False
        if self.question.question_type == "so'z keritish":
            correct = self.answer_text.strip().lower() == (self.question.enter_word or "").strip().lower()
        elif self.question.question_type == "tf":
            correct = self.answer_text.strip().lower() == (self.question.true_or_false or "").strip().lower()
        elif self.question.question_type == "test":
            correct = self.answer_text.strip().lower() == (self.question.correct_test_answer or "").strip().lower()
        return correct

    def save(self, *args, **kwargs):
        self.is_correct = self.check_correctness()
        super().save(*args, **kwargs)


class PupilReadingResult(models.Model):
    pupil = models.ForeignKey(User, on_delete=models.CASCADE)
    reading_test = models.ForeignKey(ReadingTest, on_delete=models.CASCADE)
    correct_answers = models.IntegerField()
    incorrect_answers = models.IntegerField()
    score = models.FloatField()  # IELTS ball 0.0 - 9.0
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.pupil.username} - {self.reading_test.title} natija"




# from django.db import models
# from django.core.exceptions import ValidationError
# from django.urls import reverse
# from django.utils.html import format_html
# from author.models import *
# from adminsortable.models import SortableMixin




# # -------------------------- MODELS.PY --------------------------
# class ReadingTest(models.Model):
#     title = models.CharField(max_length=255, verbose_name="Sarlavha")
#     creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Yaratuvchi")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

#     def get_question_count(self):
#         return sum(task.questions.count() for task in self.tasks.all())
#     get_question_count.short_description = "Savollar soni"

#     def clean(self):
#         super().clean()
#         total = self.get_question_count()
#         if total != 40:
#             raise ValidationError(f"Reading testda 40 ta savol bo'lishi kerak! Hozir {total} ta savol mavjud.")

#     def __str__(self):
#         return f"{self.title} ({self.get_question_count()}/40)"

#     class Meta:
#         verbose_name = "Reading Test"
#         verbose_name_plural = "Reading Testlar"
#         ordering = ['-created_at']



# class Task(models.Model):
#     CONTENT_TYPE_CHOICES = (
#         ('pdf', 'PDF File'),
#         ('direct', 'Toʻgʻridan-toʻgʻri kirish'),
#     )
#     TASK_NUMBER_CHOICES = (
#         (1, 'Topshiriq 1'),
#         (2, 'Topshiriq 2'),
#         (3, 'Topshiriq 3'),
#     )

#     reading_test = models.ForeignKey(ReadingTest, on_delete=models.CASCADE, related_name='tasks')
#     task_number = models.PositiveSmallIntegerField(choices=TASK_NUMBER_CHOICES)
#     content_type = models.CharField(
#         max_length=10,
#         choices=CONTENT_TYPE_CHOICES,
#         default='direct',
#         verbose_name="Kontent turi"
#     )
#     content_pdf = models.FileField(
#         upload_to='reading_tasks/pdfs/', 
#         blank=True, 
#         null=True,
#         verbose_name="PDF fayl",
#         help_text="PDF fayl yuklang (max 5MB)"
#     )
#     content_text = models.TextField(
#         blank=True, 
#         null=True, 
#         verbose_name="Matnli kontent",
#         help_text="Yoki to'g'ridan-to'g'ri matn kiriting"
#     )

#     def clean(self):
#         super().clean()
        
#         if self.content_type == 'pdf':
#             if not self.content_pdf:
#                 raise ValidationError("PDF tanlaganda PDF fayl yuklanishi shart.")
#             if self.content_text:
#                 raise ValidationError("PDF tanlaganda matn kiritib boʻlmaydi.")
#         elif self.content_type == 'direct':
#             if self.content_pdf:
#                 raise ValidationError("Toʻgʻridan-toʻgʻri kirish tanlaganda PDF fayl kiritib boʻlmaydi.")

#     class Meta:
#         unique_together = ('reading_test', 'task_number')
#         ordering = ['task_number']


# class TaskContentImage(models.Model):
#     task = models.ForeignKey(
#         Task, 
#         on_delete=models.CASCADE, 
#         related_name='content_images',
#         verbose_name="Task"
#     )
#     image = models.ImageField(
#         upload_to='reading_tasks/images/', 
#         verbose_name="Rasm",
#         help_text="Task uchun rasm yuklang (JPG/PNG formatida)"
#     )
#     order = models.PositiveSmallIntegerField(
#         default=0,
#         verbose_name="Tartib raqami"
#     )

#     class Meta:
#         ordering = ['order']
#         verbose_name = "Task rasmi"
#         verbose_name_plural = "Task rasmlari"
        
        

# class Question(SortableMixin):
#     QUESTION_TYPE_CHOICES = (
#         ('MC', 'Ko‘p tanlov'),
#         ('TFNG', 'True/False/Not Given'),
#         ('SHORT', 'Qisqa javob'),
#     )
    
#     task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='questions')
#     type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES)
#     text = models.TextField(verbose_name="Savol matni")
#     data = models.JSONField(verbose_name="Qo'shimcha ma'lumotlar", default=dict,
#                            help_text="Savol turiga mos ma'lumotlar (masalan, variantlar)")
#     order = models.PositiveSmallIntegerField(default=0)
#     explanation = models.TextField(blank=True, verbose_name="Tushuntirish")

#     def clean(self):
#         super().clean()
#         required_fields = {
#             'MC': {'options': list, 'correct_answer': int},
#             'TFNG': {'correct_answer': ['True', 'False', 'Not Given']},
#             'SHORT': {'max_length': int, 'correct_answer': str}
#         }
        
#         rules = required_fields.get(self.type)
#         if not rules:
#             raise ValidationError("Noto'g'ri savol turi")
            
#         for field, field_type in rules.items():
#             if field not in self.data:
#                 raise ValidationError(f"{self.get_type_display()} uchun {field} maydoni talab qilinadi!")
                
#             if isinstance(field_type, type) and not isinstance(self.data[field], field_type):
#                 raise ValidationError(f"{field} maydoni {field_type.__name__} turida bo'lishi kerak!")
                
#             if isinstance(field_type, list) and self.data[field] not in field_type:
#                 raise ValidationError(f"{field} maydoni {', '.join(field_type)} lardan biri bo'lishi kerak!")

#     class Meta:
#         ordering = ['order']
#         indexes = [
#             models.Index(fields=['task', 'order']),
#             models.Index(fields=['type']),
#         ]







