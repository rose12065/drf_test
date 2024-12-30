from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    # path('apioverview/', views.ApiOverview, name='home'),
    path('display/',views.get_user_details,name='display'),
]
