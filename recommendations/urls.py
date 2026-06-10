from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('get/', views.get_recommendations, name='get_recommendations'),
]
