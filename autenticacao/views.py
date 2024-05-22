from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import auth
from django.conf import settings
from .utils import password_is_valid, email_html
from .models import Ativacao
from hashlib import sha256
import os


def cadastro(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        
        return render(request, 'cadastro.html')


def valida_cadastro(request):
    if request.method == 'POST':
        username = request.POST.get('usuario')
        senha = request.POST.get('senha')
        email = request.POST.get('email')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('/auth/cadastro/')
        
        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.ERROR, 'Nome de usuário já existe! Por favor escolha outro.')
            return redirect('/auth/cadastro/')

        try:
            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=senha,
                                            is_active=False) # ativar através do email
            user.save()

            token = sha256(f'{username}{email}'.encode()).hexdigest()
            ativacao = Ativacao(token=token, user=user)
            ativacao.save()

            path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
            email_html(path_template, 'Cadastro confirmado', [email,], username=username, link_ativacao=f'127.0.0.1:8000/auth/ativar_conta/{token}')
            
            messages.add_message(request, messages.SUCCESS, 'Cadastro realizado com sucesso! Entre com suas credenciais.')
            return redirect('/auth/login/')
        
        except:
            messages.add_message(request, messages.ERROR, 'Erro interno do Sistema! Contate um Administrador.')
            return redirect('/auth/cadastro/')


def logar(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        
        return render(request, 'login.html')
    
    
def valida_login(request):
    if request.method == 'POST':
        username = request.POST.get('usuario')
        senha = request.POST.get('senha')

        usuario = auth.authenticate(username=username, password=senha)

        if not usuario:
            messages.add_message(request, messages.ERROR, 'Nome de usuário ou senha inválidos')
            return redirect('/auth/login/')
        
        auth.login(request, usuario)
        return redirect('/')


def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)
    
    if token.ativo:
        messages.add_message(request, messages.WARNING, 'Essa token já foi usado')
        return redirect('/auth/login/')
    
    user = User.objects.get(username=token.user.username)
    user.is_active = True
    user.save()

    token.ativo = True
    token.save()

    messages.add_message(request, messages.SUCCESS, 'Conta ativa com sucesso!')
    return redirect('/auth/login/')


def sair(request):
    auth.logout(request)
    return redirect('/auth/login/')
