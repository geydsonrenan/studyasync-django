from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
# Create your views he

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST['username']
        senha = request.POST['senha']
        confirm_senha = request.POST['confirmar_senha']
        if not senha == confirm_senha:
            messages.add_message(request, constants.ERROR, 'Senha e Confirmar Senha não coincidem')
            return redirect('/usuarios/cadastro')
        
        user = User.objects.filter(username=username)
        if user.exists():
            messages.add_message(request, constants.ERROR, 'Usuário já existe')
            return redirect('/usuarios/cadastro')
        
        try:
            User.objects.create_user(username=username, password=senha)
            return redirect('/usuarios/logar')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do servidor')
            return redirect('/usuarios/cadastro')

def logar(request):
    if request.method == 'GET':
        print('bu')
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        senha = request.POST['senha']

        user = auth.authenticate(request, username=username, password=senha)

        if user == None:
            messages.add_message(request, constants.ERROR, 'Usuário ou Senha não estão corretos')
            return redirect('/usuarios/logar')

        else:
            auth.login(request, user)
            return redirect('/flashcard/novo_flashcard')
        
def logout(request):
    auth.logout(request)
    return redirect('/usuarios/logar')
