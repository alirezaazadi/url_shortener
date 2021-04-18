from app_users import views as user_view
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'app_users'

custom_token_obtain_pair = user_view.CustomTokenObtainPairView.as_view()
token_refresh = TokenRefreshView.as_view()

urlpatterns = [
    path('token/', custom_token_obtain_pair, name='custom_token_obtain_pair'),
    path('token/refresh/', token_refresh, name='token_refresh'),
]
