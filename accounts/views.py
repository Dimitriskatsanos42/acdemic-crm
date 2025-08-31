from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)

            if form.is_valid():
                form.save()
                messages.success(request, f"Account created successfully!")
                
                return redirect('login')
        else:
            form = CustomUserCreationForm()

        context = {'form': form}
        return render(request, 'accounts/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, "Incorrect email or password. Please, try again...")
                # return redirect('login')
        
        context = {}
        return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

def indexPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        context = {}
        return render(request, 'accounts/index.html', context)

@login_required(login_url='login')
def homePage(request):
    unread_count = request.user.notifications.filter(is_read=False).count()
    # context = {'role': request.user.role, 'unread_notifications_count': unread_count}
    context = {'role': request.user.role}
    return render(request, 'accounts/home.html', context)