from django import forms
from django.contrib.auth.models import User


class StudentRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    full_name = forms.CharField(max_length=150)
    roll_number = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=20, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')

        username = cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')

        return cleaned_data


class TestForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, required=False)
    duration_minutes = forms.IntegerField(min_value=5)
    total_marks = forms.IntegerField(min_value=1, required=False)


class MCQQuestionForm(forms.Form):
    question_text = forms.CharField(widget=forms.Textarea)
    marks = forms.IntegerField(min_value=1)
    option_1 = forms.CharField(max_length=250)
    option_2 = forms.CharField(max_length=250)
    option_3 = forms.CharField(max_length=250)
    option_4 = forms.CharField(max_length=250)
    correct_option = forms.ChoiceField(
        choices=[('1', 'Option 1'), ('2', 'Option 2'), ('3', 'Option 3'), ('4', 'Option 4')]
    )


class CodingQuestionForm(forms.Form):
    question_text = forms.CharField(widget=forms.Textarea)
    marks = forms.IntegerField(min_value=1)
    sample_input = forms.CharField(widget=forms.Textarea, required=False)
    sample_output = forms.CharField(widget=forms.Textarea, required=False)
    expected_output = forms.CharField(widget=forms.Textarea, required=False)


class TestQuestionTypeForm(forms.Form):
    question_type = forms.ChoiceField(choices=[('mcq', 'MCQ'), ('coding', 'Coding')])
