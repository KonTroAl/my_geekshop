from django.urls import path, re_path

from authapp.views import logout, verify, profile, UserLoginView, UserCreateView

app_name = 'authapp'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('logout/', logout, name='logout'),
    # path('profile/<int:pk>/', UserProfileView.as_view(), name='profile'),
    path('profile/', profile, name='profile'),

    path('verify/<int:user_id>/<hash>/', verify, name='verify')
]
