from django.db import models
from mock_reading.models import IELTS
from author.models import User

class Writing(models.Model):
    ielts = models.ForeignKey(IELTS, on_delete=models.CASCADE, related_name='writings')
    title = models.CharField(max_length=255)
    allow_time = models.PositiveIntegerField(help_text="Ruxsat etilgan vaqt (daqiqa)")
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class WritingTaskFirst(models.Model):
    writing = models.ForeignKey('Writing', on_delete=models.CASCADE, related_name='task_firsts')
    title = models.CharField(max_length=255)
    pdf = models.FileField(upload_to='writing/task1/pdfs/', null=True, blank=True)
    text = models.TextField()
    img = models.ImageField(upload_to='writing/task1/images/', null=True, blank=True)
    exam_img = models.ImageField(upload_to='writing/task1/images/', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.writing.title} - Task 1"


class WritingTaskSecond(models.Model):
    writing = models.ForeignKey(Writing, on_delete=models.CASCADE, related_name='task_seconds')
    title = models.CharField(max_length=255)
    topic = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.writing.title} - Task 2"


class WritingAnswer(models.Model):
    writing = models.ForeignKey(Writing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_number = models.IntegerField(choices=[(1, "Task 1"), (2, "Task 2")])
    answer_text = models.TextField()
    score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    checked_by_ai = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - Task {self.task_number}"
