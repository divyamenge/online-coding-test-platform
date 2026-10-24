from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=150)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.user.username


class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    total_marks = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tests')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.total_marks <= 0:
            self.total_marks = sum(question.marks for question in self.questions.all())
        super().save(*args, **kwargs)


class Question(models.Model):
    QUESTION_TYPE_CHOICES = (
        ('mcq', 'MCQ'),
        ('coding', 'Coding'),
    )

    test = models.ForeignKey(Test, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, default='mcq')
    marks = models.PositiveIntegerField(default=1)
    sample_input = models.TextField(blank=True, default='')
    sample_output = models.TextField(blank=True, default='')
    expected_output = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:80]

    def get_correct_option(self):
        if self.question_type != 'mcq':
            return None
        return self.options.filter(is_correct=True).first()


class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=250)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text


class TestAttempt(models.Model):
    student = models.ForeignKey(Student, related_name='attempts', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, related_name='attempts', on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)
    is_submitted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.student.user.username} - {self.test.title}'


class Submission(models.Model):
    attempt = models.ForeignKey(TestAttempt, related_name='submissions', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='submissions', on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, null=True, blank=True, on_delete=models.SET_NULL)
    submitted_answer = models.TextField(blank=True, default='')
    is_correct = models.BooleanField(default=False)
    score_earned = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.attempt.student.user.username} - {self.question.id}'
