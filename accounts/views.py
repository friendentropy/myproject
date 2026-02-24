from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm

@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")


@login_required
def profile_edit(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("accounts:profile")

    return render(request, "accounts/profile_edit.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("products:product_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect("accounts:login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})



def login_view(request):
    if request.user.is_authenticated:
        # If already logged in, send user to dashboard instead of products
        return redirect("dashboard_home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Welcome back!")

            # ✔ Respect ?next=/some/url
            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            # ✔ Default: dashboard
            return redirect("dashboard_home")

        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})




def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")
