from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),

    path('api/user/', views.UserDetailView.as_view(), name='user-detail'),

    path('api/resume/upload/', views.ResumeUploadView.as_view(), name='resume_upload'),
    path('api/resumes/', views.ResumeListView.as_view(), name='resume_list'),
    path('api/resume/<str:resume_id>/', views.ResumeDetailView.as_view(), name='resume-detail'),

    path('api/job/create/', views.JobListingCreateView.as_view(), name='job-create'),
    path('api/job/<int:job_id>/', views.JobListingDetailView.as_view(), name='job-detail'),
    path('api/job/<int:job_id>/update/', views.JobListingUpdateView.as_view(), name='job-update'),
    path('api/job/<int:job_id>/delete/', views.JobListingDeleteView.as_view(), name='job-delete'),
    path('api/job/list/', views.JobListingListView.as_view(), name='job-list'),
]
