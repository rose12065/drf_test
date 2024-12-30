import uuid
from django.shortcuts import get_object_or_404, render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf import settings
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import AllowAny
from .models import CustomUser 
import boto3
import json
import base64
@api_view(['GET', 'POST'])
def register_user(request):
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

# @api_view(['GET'])
# def ApiOverview(request):
#     api_urls = {
#         'all_items': '/',
#         'Search by Category': '/?category=category_name',
#         'Search by Subcategory': '/?subcategory=category_name',
#         'Add': '/create',
#         'Update': '/update/pk',
#         'Delete': '/item/pk/delete'
#     }
 
#     return Response(api_urls)

@api_view(['GET'])
def get_user_details(request):
    print(request)
    print("dhjdgs")
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
    print(type(image))
    profile_image=image.get("Body").read()
    # body = profile_image.decode('utf-8')
    print("Body",profile_image)
    # return HttpResponse(image_data, content_type="image/jpeg")

    dataStr = json.dumps(profile_image)

    base64EncodedStr = base64.b64encode(dataStr.encode('utf-8'))
    # image_p=json.dumps(image)
    # image1 = json.loads(image_p)
    # print("hgajs",image1)
    return Response({
        "username": user.username,
        "email": user.email,
        "date_of_birth": user.date_of_birth,
        "role": user.role,
        "profile_picture": base64EncodedStr
    }, status=200)