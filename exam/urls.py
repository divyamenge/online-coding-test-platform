from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_student, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tests/new/', views.test_form, name='test_create'),
    path('tests/<int:test_id>/edit/', views.test_form, name='test_edit'),
    path('tests/<int:test_id>/delete/', views.test_delete, name='test_delete'),
    path('tests/<int:test_id>/question/new/', views.question_form, name='question_create'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('tests/<int:test_id>/', views.student_test_view, name='student_test_view'),
    path('tests/<int:test_id>/submit/', views.submit_test, name='submit_test'),
    path('results/<int:attempt_id>/', views.results_view, name='results_view'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
