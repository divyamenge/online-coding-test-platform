from django import forms


class TestQuestionTypeForm(forms.Form):
    question_type = forms.ChoiceField(choices=[('mcq', 'MCQ'), ('coding', 'Coding')])
