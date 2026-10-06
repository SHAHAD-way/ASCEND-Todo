from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import (
    RegisterForm,
    CustomPasswordChangeForm,
    ProfilePictureForm
)

from .models import Profile

from todos.models import Todo


def register(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            Profile.objects.create(
                user=user
            )

            messages.success(
                request,
                'Account created successfully! Please login. ✅'
            )

            return redirect('login')

    else:

        form = RegisterForm()

    return render(
        request,
        'register.html',
        {'form': form}
    )


def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            messages.success(
                request,
                'Welcome back! Login successful. 👋'
            )

            return redirect('dashboard')

        else:

            messages.error(
                request,
                'Invalid username or password. ❌'
            )

    return render(
        request,
        'login.html'
    )


def logout_view(request):

    logout(request)

    messages.info(
        request,
        'You have been logged out successfully. 👋'
    )

    return redirect('login')


@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        form = ProfilePictureForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Profile picture updated successfully! 🖼️'
            )

            return redirect('profile')

    else:

        form = ProfilePictureForm(
            instance=profile
        )

    total_todos = Todo.objects.filter(
        user=request.user
    ).count()

    completed_todos = Todo.objects.filter(
        user=request.user,
        completed=True
    ).count()

    pending_todos = Todo.objects.filter(
        user=request.user,
        completed=False
    ).count()

    return render(
        request,
        'profile.html',
        {
            'profile': profile,
            'form': form,
            'total_todos': total_todos,
            'completed_todos': completed_todos,
            'pending_todos': pending_todos
        }
    )


@login_required
def change_password(request):

    if request.method == 'POST':

        form = CustomPasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            login(
                request,
                user
            )

            messages.success(
                request,
                'Your password was changed successfully! 🔐'
            )

            return redirect('profile')

    else:

        form = CustomPasswordChangeForm(
            request.user
        )

    return render(
        request,
        'change_password.html',
        {
            'form': form
        }
    )