from django.urls import path
from . import views

urlpatterns = [
    path('pacientes/', views.pacientes , name='pacientes'),
    path('valida_paciente/', views.valida_paciente, name='valida_paciente'),
    path('dados_paciente/', views.dados_paciente_listar, name='dados_paciente_listar'),
    path('dados_paciente/<int:paciente_id>/', views.dados_paciente, name='dados_paciente'),
    path('valida_dados/<int:paciente_id>/', views.valida_dados, name='valida_dados'),
    path('grafico_peso/<int:paciente_id>/', views.grafico_peso, name='grafico_peso')

]
