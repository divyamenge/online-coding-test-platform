from django.contrib import admin
from .models import Student, Test, Question, Option, TestAttempt, Submission

admin.site.register(Student)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(TestAttempt)
admin.site.register(Submission)
