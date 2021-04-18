from app_shortener.views import *
from django.urls import path

app_name = 'app_shortener'

urlpatterns = [
    path('generate/', create_short_url),
    path('statistics/<str:short_url>/', statistics),
    path('r/<str:short_url>/', redirect_view),
]
