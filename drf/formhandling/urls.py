from django.urls import path

from . import views

urlpatterns = [
    path('registerclass/', views.UserRegistrationView.as_view(), name='register_user'),
    path('register/', views.register_user, name='register_user'),
    path('ApiItem/', views.ApiItem, name='ApiItem'),
    path('display/',views.get_user_details,name='display'),
    path('users-list/', views.UserListView.as_view(), name='user-list'),
    # path('alert/', views.AlertAPIView.as_view(), name='alert'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('reset-password/',views.RequestPasswordResetView.as_view(),name='reset-password'),
    path("reset-password/<str:uid>/<str:token>/", views.ResetPasswordView.as_view(), name="reset-password"),
    

    
]
