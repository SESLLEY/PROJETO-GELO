from django.urls import path
from . import views

urlpatterns = [
    path('', views.venda_rapida, name='venda_rapida'),
    path('painel/', views.painel, name='painel'),
    path('relatorio-clientes/', views.relatorio_clientes, name='relatorio_clientes'),
]