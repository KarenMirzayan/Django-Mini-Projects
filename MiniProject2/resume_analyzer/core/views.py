from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsRecruiter
from .models import Resume, JobListing, User
from .ai_processor import extract_text, analyze_resume
from .schemas import (
    ResumeUploadInput, ResumeAnalysisOutput, ResumeResponse,
    JobListingCreate, JobListingUpdate, JobListingResponse,
    UserRegisterInput, UserRegisterResponse, VerifyEmailInput, ResumeResponseList
)
from celery import shared_task
from bson import ObjectId
from mongoengine.errors import DoesNotExist
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from .serializers import UserSerializer


@shared_task
def process_resume(resume_id, skills_required=None):
    try:
        print(f"Task received for resume_id: {resume_id}")
        resume = Resume.objects.get(id=ObjectId(resume_id))
        print(f"Found resume with ID: {resume.id}")
        if resume.file is None:
            raise ValueError("No file associated with this resume")
        file_bytes = resume.file.read()
        print(f"File content length: {len(file_bytes)} bytes")
        if not file_bytes:
            raise ValueError("File content is empty")
        text = extract_text(file_bytes, resume.file.name)
        print(f"Extracted text: {text[:50]}...")
        analysis = analyze_resume(text, skills_required)
        analysis_output = ResumeAnalysisOutput(**analysis)
        print(f"Analysis result: {analysis_output.model_dump()}")
        resume.extracted_data = analysis_output.model_dump()
        resume.score = analysis_output.score
        resume.save()
        print(f"Saved resume with extracted_data: {resume.extracted_data}, score: {resume.score}")
    except Exception as e:
        print(f"Task failed: {str(e)}")
        raise


class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.email_verified:
            return Response({'error': 'Please verify your email first'}, status=403)
        try:
            file_obj = request.FILES.get('file')
            if not file_obj:
                return Response({'error': 'No file provided'}, status=400)
            file_bytes = file_obj.read()
            job_id = request.data.get('job_id')
            skills_required = None
            if job_id:
                try:
                    job_listing = JobListing.objects.get(id=int(job_id))
                    skills_required = job_listing.skills_required
                except JobListing.DoesNotExist:
                    return Response({'error': 'Job listing not found'}, status=404)

            input_data = ResumeUploadInput(file=file_bytes, job_id=job_id)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

        resume = Resume(user_id=request.user.id)
        resume.file.put(file_bytes, content_type=file_obj.content_type, filename=file_obj.name)
        try:
            resume.save()
            resume_id = str(resume.id)
            print(f"Saved resume with ID: {resume_id}")
        except Exception as e:
            print(f"Failed to save resume: {str(e)}")
            return Response({'error': 'Failed to save resume'}, status=500)

        process_resume.delay(resume_id, skills_required)
        return Response({'message': 'Resume uploaded, processing started', 'resume_id': resume_id}, status=201)


class ResumeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, resume_id):
        try:
            resume = Resume.objects.get(id=ObjectId(resume_id))
            if resume.user_id != request.user.id:
                return Response({'error': 'You do not have permission to view this resume'}, status=403)

            # Debug: Log the raw extracted_data
            print(f"Raw extracted_data: {resume.extracted_data}")
            if not resume.extracted_data:
                return Response({'error': 'Extracted data is empty'}, status=400)

            analysis = ResumeAnalysisOutput(**resume.extracted_data)
            print(f"Validated analysis: {analysis.model_dump()}")

            response = ResumeResponse(
                resume_id=str(resume.id),
                user_id=resume.user_id,
                analysis=analysis,
                score=resume.score
            )
            return Response(response.model_dump(), status=200)
        except DoesNotExist:
            return Response({'error': 'Resume not found'}, status=404)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            print(f"Error retrieving resume: {str(e)}")
            return Response({'error': 'An error occurred while retrieving the resume'}, status=500)


class ResumeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            resumes = Resume.objects.filter(user_id=request.user.id)
            response_data = []

            for resume in resumes:
                response_item = ResumeResponseList(
                    resume_id=str(resume.id),
                    score=resume.score
                )
                response_data.append(response_item.model_dump())

            return Response(response_data, status=200)

        except Exception as e:
            print(f"Error retrieving resumes: {str(e)}")
            return Response({'error': 'An error occurred while retrieving resumes'}, status=500)


class JobListingCreateView(APIView):
    permission_classes = [IsAuthenticated, IsRecruiter]

    def post(self, request):
        if not request.user.email_verified:
            return Response({'error': 'Please verify your email first'}, status=403)
        try:
            input_data = JobListingCreate(**request.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

        job_listing = JobListing(
            title=input_data.title,
            description=input_data.description,
            skills_required=input_data.skills_required,
            recruiter=request.user
        )
        try:
            job_listing.save()
            response = JobListingResponse(
                job_id=job_listing.id,
                title=job_listing.title,
                description=job_listing.description,
                skills_required=job_listing.skills_required,
                recruiter_id=job_listing.recruiter.id,
                created_at=job_listing.created_at,
                updated_at=job_listing.updated_at
            )
            return Response(response.model_dump(), status=201)
        except Exception as e:
            print(f"Failed to save job listing: {str(e)}")
            return Response({'error': 'Failed to save job listing'}, status=500)


class JobListingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            job_listing = JobListing.objects.get(id=int(job_id))
            if request.user.role == 'recruiter' and job_listing.recruiter.id != request.user.id:
                return Response({'error': 'You do not have permission to view this job listing'}, status=403)
            response = JobListingResponse(
                job_id=job_listing.id,
                title=job_listing.title,
                description=job_listing.description,
                skills_required=job_listing.skills_required,
                recruiter_id=job_listing.recruiter.id,
                created_at=job_listing.created_at,
                updated_at=job_listing.updated_at
            )
            return Response(response.model_dump(), status=200)
        except JobListing.DoesNotExist:
            return Response({'error': 'Job listing not found'}, status=404)
        except Exception as e:
            print(f"Error retrieving job listing: {str(e)}")
            return Response({'error': 'An error occurred while retrieving the job listing'}, status=500)


class JobListingUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsRecruiter]

    def put(self, request, job_id):
        if not request.user.email_verified:
            return Response({'error': 'Please verify your email first'}, status=403)
        try:
            job_listing = JobListing.objects.get(id=int(job_id))
            if job_listing.recruiter.id != request.user.id:
                return Response({'error': 'You do not have permission to update this job listing'}, status=403)

            input_data = JobListingUpdate(**request.data)
            if input_data.title is not None:
                job_listing.title = input_data.title
            if input_data.description is not None:
                job_listing.description = input_data.description
            if input_data.skills_required is not None:
                job_listing.skills_required = input_data.skills_required
            job_listing.save()

            response = JobListingResponse(
                job_id=job_listing.id,
                title=job_listing.title,
                description=job_listing.description,
                skills_required=job_listing.skills_required,
                recruiter_id=job_listing.recruiter.id,
                created_at=job_listing.created_at,
                updated_at=job_listing.updated_at
            )
            return Response(response.model_dump(), status=200)
        except JobListing.DoesNotExist:
            return Response({'error': 'Job listing not found'}, status=404)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            print(f"Failed to update job listing: {str(e)}")
            return Response({'error': 'Failed to update job listing'}, status=500)


class JobListingDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsRecruiter]

    def delete(self, request, job_id):
        if not request.user.email_verified:
            return Response({'error': 'Please verify your email first'}, status=403)
        try:
            job_listing = JobListing.objects.get(id=int(job_id))
            if job_listing.recruiter.id != request.user.id:
                return Response({'error': 'You do not have permission to delete this job listing'}, status=403)
            job_listing.delete()
            return Response({'message': 'Job listing deleted successfully'}, status=204)
        except JobListing.DoesNotExist:
            return Response({'error': 'Job listing not found'}, status=404)
        except Exception as e:
            print(f"Failed to delete job listing: {str(e)}")
            return Response({'error': 'Failed to delete job listing'}, status=500)


class JobListingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role == 'recruiter':
                job_listings = JobListing.objects.filter(recruiter=request.user)
            else:
                job_listings = JobListing.objects.all()

            response = [
                JobListingResponse(
                    job_id=job.id,
                    title=job.title,
                    description=job.description,
                    skills_required=job.skills_required,
                    recruiter_id=job.recruiter.id,
                    created_at=job.created_at,
                    updated_at=job.updated_at
                ) for job in job_listings
            ]
            return Response([job.model_dump() for job in response], status=200)
        except Exception as e:
            print(f"Error retrieving job listings: {str(e)}")
            return Response({'error': 'An error occurred while retrieving job listings'}, status=500)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            input_data = UserRegisterInput(**request.data)
            if User.objects.filter(username=input_data.username).exists():
                return Response({'error': 'Username already taken'}, status=400)
            if User.objects.filter(email=input_data.email).exists():
                return Response({'error': 'Email already registered'}, status=400)
            if input_data.role == 'admin':
                return Response({'error': 'Admin role cannot be self-assigned'}, status=403)

            token = str(uuid.uuid4())
            user = User(
                username=input_data.username,
                email=input_data.email,
                role=input_data.role,
                password=make_password(input_data.password),
                verification_token=token
            )
            user.save()

            verification_link = f"http://localhost:5173/api/verify-email/?token={token}"
            subject = "Verify Your Email Address"
            message = f"Hi {user.username},\n\nPlease verify your email by clicking this link: {verification_link}\n\nThanks,\nResume Analyzer Team"
            send_mail(subject, message, from_email=None, recipient_list=[user.email], fail_silently=False)

            response = UserRegisterResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                message="Registration successful. Please check your email to verify your account."
            )
            return Response(response.model_dump(), status=201)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            print(f"Registration failed: {str(e)}")
            return Response({'error': 'Failed to register user'}, status=500)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            input_data = VerifyEmailInput(token=request.query_params.get('token'))
            user = User.objects.get(verification_token=input_data.token)
            if user.email_verified:
                return Response({'message': 'Email already verified'}, status=200)

            user.email_verified = True
            user.verification_token = None
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Email verified successfully',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }, status=200)
        except User.DoesNotExist:
            return Response({'error': 'Invalid or expired verification token'}, status=400)
        except Exception as e:
            print(f"Email verification failed: {str(e)}")
            return Response({'error': 'Failed to verify email'}, status=500)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
