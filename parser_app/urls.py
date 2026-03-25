from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('parse/', views.parse_article, name='parse'),
    path('result/<int:paper_id>/', views.result, name='result'),
]