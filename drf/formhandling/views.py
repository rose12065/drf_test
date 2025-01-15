import base64
import uuid

import boto3
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .services import EmailService, PasswordResetTokenService, ResetPasswordService, UserValidationService
# from formhandling.tasks import add
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from drf import settings

from .models import CustomUser, Item
from .serializers import (ItemSerializer, LoginSerializer,
                          UserRegistrationSerializer)
# from .services.alert_service import AlertService


# user detials inserting and the file is uploaded from the frontend 
@api_view(['GET', 'POST'])
def register_user(request):
    # permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    if request.method == 'POST':
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        date_of_birth = request.data.get('date_of_birth')
        role = request.data.get('role')
        profile_picture = request.FILES.get('profile_picture')  
      
        if not profile_picture:
            return Response({'error': 'No profile picture provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if not username or not email or not password:
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)
       
        try:
            file_name = f"profile_pictures/{uuid.uuid4()}-{profile_picture.name}"
            
            minio_client = boto3.client(
                's3',
                endpoint_url=f"http{'s' if settings.MINIO_STORAGE_USE_HTTPS else ''}://{settings.MINIO_STORAGE_ENDPOINT}",
                aws_access_key_id=settings.MINIO_STORAGE_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_STORAGE_SECRET_KEY,
            )
            minio_client.put_object(
                Bucket=settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                Key=file_name,
                Body=profile_picture,
                ContentType=profile_picture.content_type
            )
        except Exception as e:
            return Response({'error': 'Failed to upload image to MinIO.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user = CustomUser.objects.create(
            username=username,
            email=email,
            password=password, 
            date_of_birth=date_of_birth,
            role=role,
            profile_picture=file_name
        )
        user.set_password(password)
        user.save()
        return Response({'message': 'User registered successfully!', 'user_id': user.id}, status=status.HTTP_201_CREATED)

    return Response({'message': 'Please submit your details.'}, status=status.HTTP_200_OK)


# class based view for user registration  file upload using the data URI 
@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(APIView):
    def post(self, request):
        print("Entered the function")
        
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            validated_data = serializer.validated_data
            
            # Extract profile_picture and decode from Base64
            profile_picture = validated_data.pop('profile_picture', None)
            
            # Log the incoming profile_picture data for debugging
            print("Received profile_picture:", profile_picture)
            
            if profile_picture and isinstance(profile_picture, str) and profile_picture.startswith('data:image'):
                try:
                    # Decode data URI into a file-like object
                    format, imgstr = profile_picture.split(';base64,')
                    ext = format.split('/')[-1]
                    decoded_image = ContentFile(base64.b64decode(imgstr), name=f"profile_picture.{ext}")
                    
                    # Upload the file to MinIO
                    file_name = f"profile_pictures/{uuid.uuid4()}.{ext}"
                    minio_client = boto3.client(
                        's3',
                        endpoint_url=f"http{'s' if settings.MINIO_STORAGE_USE_HTTPS else ''}://{settings.MINIO_STORAGE_ENDPOINT}",
                        aws_access_key_id=settings.MINIO_STORAGE_ACCESS_KEY,
                        aws_secret_access_key=settings.MINIO_STORAGE_SECRET_KEY,
                    )
                    minio_client.put_object(
                        Bucket=settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                        Key=file_name,
                        Body=decoded_image.file,
                        ContentType=f"image/{ext}"
                    )
                    
                    # Add the MinIO file path back to validated_data
                    validated_data['profile_picture'] = file_name
                    
                except Exception as e:
                    # Log exception for debugging
                    print("Error uploading image to MinIO:", e)
                    return Response(
                        {'error': 'Failed to upload image to MinIO.', 'details': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response(
                    {'error': 'Invalid or missing profile picture.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the user
            user = serializer.create(validated_data)
            return Response(
                {'message': 'User registered successfully!', 'user_id': user.id},
                status=status.HTTP_201_CREATED
            )
        
        # Log serializer errors for debugging
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# user details fetching
@api_view(['GET'])
def get_user_details(request):
    if request.query_params:
        user_id =request.query_params.get("user_id")
        user=CustomUser.objects.filter(id=user_id).first()
        profile_picture_url=user.profile_picture
    else:
        user=CustomUser.objects.all()
        profile_picture_url=user.profile_picture
        
    # profile_picture_url = f"http://{settings.MINIO_STORAGE_ENDPOINT}/{settings.MINIO_STORAGE_MEDIA_BUCKET_NAME}/{user.profile_picture}"
    minio_client = boto3.client(
                's3',
                endpoint_url=f"http{'s' if settings.MINIO_STORAGE_USE_HTTPS else ''}://{settings.MINIO_STORAGE_ENDPOINT}",
                aws_access_key_id=settings.MINIO_STORAGE_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_STORAGE_SECRET_KEY,
            )  
    
    image= minio_client.get_object(
            Bucket=settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
            Key=profile_picture_url
        )
    # convert the image url in minio to base64
    profile_image = image["Body"].read()
    ext = profile_picture_url.split('.')[-1]
    # Convert the binary data to a base64-encoded string
    base64_encoded_str = f"data:image/{ext};base64,{base64.b64encode(profile_image).decode('utf-8')}"  # Decode as UTF-8 to get a string
 
    return Response({
        "username": user.username,
        "email": user.email,
        "date_of_birth": user.date_of_birth,
        "role": user.role,
        "profile_picture": base64_encoded_str
    }, status=200)
    


@api_view(['POST'])
def ApiItem(request):
    try:
        if request.method == 'POST':
            serializer = ItemSerializer(data=request.data)
            
            if serializer.is_valid():
                # Check if an item with the same data already exists
                category = serializer.validated_data.get('category')
                subcategory = serializer.validated_data.get('subcategory')
                name = serializer.validated_data.get('name')
                amount = serializer.validated_data.get('amount')
                
                if Item.objects.filter(category=category, subcategory=subcategory, name=name, amount=amount).exists():
                    return Response(
                        {'error': 'Item already exists with the same details.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Save the validated data to the database
                item = serializer.save()
                return Response(
                    {'message': 'Item inserted successfully!', 'item_id': item.id},
                    status=status.HTTP_201_CREATED
                )
            
            # Handle validation errors explicitly
            return Response(
                {'error': 'Validation failed', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle unsupported HTTP methods
        return Response(
            {'error': 'Invalid request method. Only POST is allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    except Exception as e:
        return Response(
            {'error': 'An unexpected error occurred', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# def add_numbers(request):
#     result = add.delay(10, 20)  # The task will be executed asynchronously by Celery
#     return JsonResponse({"task_id": result.id})

class UserListView(APIView):
    """
    A view to fetch all users from the database along with their profile pictures.
    """
    def get(self, request):
        # Fetch all users
        users = CustomUser.objects.all()
        
        if not users.exists():
            return Response({"message": "No users found."}, status=status.HTTP_404_NOT_FOUND)
        
        minio_client = boto3.client(
            's3',
            endpoint_url=f"http{'s' if settings.MINIO_STORAGE_USE_HTTPS else ''}://{settings.MINIO_STORAGE_ENDPOINT}",
            aws_access_key_id=settings.MINIO_STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_STORAGE_SECRET_KEY,
        )
        
        user_list = []
        
        for user in users:
            profile_picture_url = user.profile_picture
            base64_encoded_str = None
            
            # Attempt to fetch the profile picture from MinIO and convert to Base64
            if profile_picture_url:
                try:
                    image = minio_client.get_object(
                        Bucket=settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                        Key=profile_picture_url
                    )
                    profile_image = image["Body"].read()
                    ext = profile_picture_url.split('.')[-1]
                    base64_encoded_str = f"data:image/{ext};base64,{base64.b64encode(profile_image).decode('utf-8')}"
                except Exception as e:
                    # Log the error if image fetch fails
                    print(f"Error fetching profile picture for user {user.username}: {e}")
            
            # Append user details to the list
            user_list.append({
                "id":user.id,
                "username": user.username,
                "email": user.email,
                "date_of_birth": user.date_of_birth,
                "role": user.role,
                "profile_picture": base64_encoded_str
            })
        
        return Response(user_list, status=status.HTTP_200_OK)


# class AlertAPIView(APIView):
#     def post(self, request):
#         """
#         Send alerts (Email/SMS) to a user.
#         """
#         user_id = request.data.get("user_id")
#         send_email = request.data.get("send_email", False)
#         send_sms = request.data.get("send_sms", False)
#         phone_number= '+91 7306350738'

#         try:
#             user = CustomUser.objects.get(id=user_id)
#             alert_service = AlertService()
#             results = {}

#                 # Send email
#             if send_email:
#                 email_success, email_message = alert_service.send_email(
#                         "Alert Notification",
#                         "This is an alert message.",
#                         user.email
#                     )
#                 results['email'] = email_message

#                 # Send SMS
#             if send_sms:
#                     sms_success, sms_message = alert_service.send_sms(
#                         '+91 7306350738',
#                         "This is an alert message."
#                     )
#                     results['sms'] = sms_message
#             print(results)
#             return Response(results, status=status.HTTP_200_OK)
#         except CustomUser.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
        
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Extract credentials from the request
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            try:
                # Validate user using the UserValidationService
                user_validation_service = UserValidationService(email, password)
                user = user_validation_service.validate()

                # Generate JWT tokens on successful validation
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'message': "Login successful."
                }, status=status.HTTP_200_OK)

            except ValueError as e:
                # Handle validation errors (e.g., invalid credentials, account lockout)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")
        email_service = EmailService()
        token_service = PasswordResetTokenService()
        reset_service = ResetPasswordService(email_service, token_service)

        try:
            reset_service.request_password_reset(email, CustomUser)
            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request, uid, token):
        new_password = request.data.get("password")
        email_service = EmailService()
        token_service = PasswordResetTokenService()
        reset_service = ResetPasswordService(email_service, token_service)

        try:
            reset_service.reset_password(uid, token, new_password, CustomUser)
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)   