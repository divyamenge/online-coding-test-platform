from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.utils import timezone
from django.http import HttpResponseForbidden

from .forms import StudentRegistrationForm, TestForm, MCQQuestionForm, CodingQuestionForm, TestQuestionTypeForm
from .models import Student, Test, Question, Option, TestAttempt, Submission


def normalize_text(value):
    return ' '.join(str(value or '').strip().split()).lower()


def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('student_dashboard')
    return render(request, 'home.html')


def register_student(request):
    if request.user.is_authenticated:
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            Student.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                roll_number=form.cleaned_data['roll_number'],
                phone=form.cleaned_data['phone'],
            )
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
@user_passes_test(lambda user: user.is_staff)
def admin_dashboard(request):
    tests = Test.objects.all().prefetch_related('questions').order_by('-created_at')
    attempts = TestAttempt.objects.select_related('student__user', 'test').order_by('-submitted_at', '-score')
    context = {
        'tests': tests,
        'attempts': attempts,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
@user_passes_test(lambda user: user.is_staff)
def test_form(request, test_id=None):
    instance = Test.objects.filter(pk=test_id).first() if test_id else None
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            if instance:
                instance.title = form.cleaned_data['title']
                instance.description = form.cleaned_data['description']
                instance.duration_minutes = form.cleaned_data['duration_minutes']
                if form.cleaned_data.get('total_marks'):
                    instance.total_marks = form.cleaned_data['total_marks']
                instance.save()
            else:
                instance = Test.objects.create(
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    duration_minutes=form.cleaned_data['duration_minutes'],
                    total_marks=form.cleaned_data.get('total_marks') or 0,
                    created_by=request.user,
                )
            return redirect('admin_dashboard')
    else:
        form = TestForm(initial={
            'title': instance.title if instance else '',
            'description': instance.description if instance else '',
            'duration_minutes': instance.duration_minutes if instance else 30,
            'total_marks': instance.total_marks if instance else 0,
        }) if instance else TestForm(initial={'duration_minutes': 30})
    return render(request, 'test_form.html', {'form': form, 'test': instance})


@login_required
@user_passes_test(lambda user: user.is_staff)
def test_delete(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    test.delete()
    return redirect('admin_dashboard')


@login_required
@user_passes_test(lambda user: user.is_staff)
def question_form(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    qtype_form = TestQuestionTypeForm(request.POST or None)
    mcq_form = MCQQuestionForm(request.POST or None)
    coding_form = CodingQuestionForm(request.POST or None)

    if request.method == 'POST':
        if 'question_type' in request.POST:
            selected_type = request.POST.get('question_type')
            if selected_type == 'mcq':
                if mcq_form.is_valid():
                    question = Question.objects.create(
                        test=test,
                        question_type='mcq',
                        question_text=mcq_form.cleaned_data['question_text'],
                        marks=mcq_form.cleaned_data['marks'],
                    )
                    for idx in range(1, 5):
                        option_text = mcq_form.cleaned_data[f'option_{idx}']
                        is_correct = str(idx) == mcq_form.cleaned_data['correct_option']
                        Option.objects.create(question=question, option_text=option_text, is_correct=is_correct)
                    return redirect('admin_dashboard')
            elif selected_type == 'coding':
                if coding_form.is_valid():
                    Question.objects.create(
                        test=test,
                        question_type='coding',
                        question_text=coding_form.cleaned_data['question_text'],
                        marks=coding_form.cleaned_data['marks'],
                        sample_input=coding_form.cleaned_data['sample_input'],
                        sample_output=coding_form.cleaned_data['sample_output'],
                        expected_output=coding_form.cleaned_data['expected_output'],
                    )
                    return redirect('admin_dashboard')

    return render(
        request,
        'question_form.html',
        {
            'test': test,
            'qtype_form': qtype_form,
            'mcq_form': mcq_form,
            'coding_form': coding_form,
        },
    )


@login_required
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    tests = Test.objects.filter(is_active=True).order_by('-created_at')
    attempts = TestAttempt.objects.filter(student=student).order_by('-submitted_at', '-started_at')
    return render(request, 'student_dashboard.html', {'tests': tests, 'student': student, 'attempts': attempts})


@login_required
def student_test_view(request, test_id):
    student = get_object_or_404(Student, user=request.user)
    test = get_object_or_404(Test, pk=test_id)
    attempt = TestAttempt.objects.filter(student=student, test=test).order_by('-started_at').first()

    if attempt and attempt.is_submitted:
        return redirect('results_view', attempt_id=attempt.id)

    if not attempt:
        attempt = TestAttempt.objects.create(student=student, test=test, started_at=timezone.now())

    questions = test.questions.all().order_by('id')
    remaining_seconds = max(0, int((attempt.started_at.timestamp() + (test.duration_minutes * 60)) - timezone.now().timestamp()))
    return render(request, 'test_attempt.html', {
        'test': test,
        'attempt': attempt,
        'questions': questions,
        'remaining_seconds': remaining_seconds,
    })


@login_required
def submit_test(request, test_id):
    if request.method != 'POST':
        return redirect('student_dashboard')

    student = get_object_or_404(Student, user=request.user)
    test = get_object_or_404(Test, pk=test_id)
    attempt = TestAttempt.objects.filter(student=student, test=test).order_by('-started_at').first()
    if not attempt:
        attempt = TestAttempt.objects.create(student=student, test=test, started_at=timezone.now())

    total_score = 0
    for question in test.questions.all():
        if question.question_type == 'mcq':
            selected_id = request.POST.get(f'question_{question.id}')
            selected_option = None
            if selected_id:
                selected_option = question.options.filter(pk=selected_id).first()
            is_correct = bool(selected_option and selected_option.is_correct)
            submission = Submission.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option,
                submitted_answer=str(selected_id or ''),
                is_correct=is_correct,
                score_earned=question.marks if is_correct else 0,
            )
            total_score += submission.score_earned
        else:
            submitted_answer = request.POST.get(f'coding_{question.id}', '')
            correct = normalize_text(submitted_answer) == normalize_text(question.expected_output)
            score_earned = question.marks if correct else 0
            total_score += score_earned
            Submission.objects.create(
                attempt=attempt,
                question=question,
                submitted_answer=submitted_answer,
                is_correct=correct,
                score_earned=score_earned,
            )

    attempt.score = total_score
    attempt.is_submitted = True
    attempt.submitted_at = timezone.now()
    attempt.save()

    return redirect('results_view', attempt_id=attempt.id)


@login_required
def results_view(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, pk=attempt_id, student__user=request.user)
    submissions = attempt.submissions.select_related('question', 'selected_option').all()
    return render(request, 'results.html', {'attempt': attempt, 'submissions': submissions})


@login_required
def leaderboard(request):
    leaderboard_data = []
    students = Student.objects.annotate(total_score=Sum('attempts__score', filter=Q(attempts__is_submitted=True))).order_by('-total_score', 'user__username')
    previous_score = None
    current_rank = 1
    for i, student in enumerate(students[:10], start=1):
        if previous_score is not None and student.total_score != previous_score:
            current_rank = i
        leaderboard_data.append({
            'student': student,
            'score': student.total_score or 0,
            'rank': current_rank,
        })
        previous_score = student.total_score
    return render(request, 'leaderboard.html', {'leaderboard_data': leaderboard_data})
