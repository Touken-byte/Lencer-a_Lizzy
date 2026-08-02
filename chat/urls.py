from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_clienta, name='chat_clienta'),
]