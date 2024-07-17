from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('secteur')
        else:
            messages.error(request, 'Erreur de connexion Veuillez reessayez s\'il vous plaît ..!')
            return redirect('login')
    return render(request, 'accounts/login.html')


def logout_user(request):
    logout(request)
    return redirect('accueil')
