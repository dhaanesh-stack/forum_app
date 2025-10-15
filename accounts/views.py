from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import SignUpForm


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # no need to alias to auth_login
            return redirect("home")
    else:
        form = SignUpForm()
    
    return render(request, "signup.html", {"form": form})
