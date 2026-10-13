from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationForm, VerifyCodeForm
import random
from utils import send_otp_code
from .models import OtpCode, User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta



class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = "accounts/register.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            random_code = random.randint(1000, 9999)

            sms_sent = send_otp_code(
                phone_number=form.cleaned_data["phone_number"],
                code=random_code
            )
            if not sms_sent:
                messages.error(
                    request,
                    "Sending the verification code failed. Please try again.",
                    "danger"
                )
                return render(
                    request,
                    self.template_name,
                    {"form": form}
                )

            OtpCode.objects.filter(
                phone_number=form.cleaned_data["phone_number"]
            ).delete()

            OtpCode.objects.create(
                phone_number=form.cleaned_data["phone_number"],
                code=str(random_code)
            )
            request.session["user_registration_info"] = {
                "phone_number": form.cleaned_data["phone_number"],
                "email":form.cleaned_data["email"],
                "full_name":form.cleaned_data["full_name"],
                "password":form.cleaned_data["password"]
            }
            messages.success(
                request,
                "We sent you an activation code.",
                "success"
            )
            return redirect("accounts:verify_code")
        return render(request, self.template_name, {"form": form})



class UserRegistrationVerifyCodeView(View):
    form_class = VerifyCodeForm

    def get(self, request):
        user_session = request.session.get("user_registration_info")

        if not user_session:
            messages.error(request, "Please register first", "danger")
            return redirect("accounts:user_register")

        form = self.form_class()
        return render(request, "accounts/verify.html", {"form": form})

    def post(self, request):
        user_session = request.session.get("user_registration_info")
        if not user_session:
            messages.error(request, "Please Register first", "danger")
            return redirect("accounts:user_register")

        code_instance = OtpCode.objects.filter(
            phone_number=user_session["phone_number"]
        ).first()
        if code_instance is None:
            request.session.pop("user_registration_info", None)
            messages.error(
                request,
                "Verification code not found. Please register again",
                "danger"
            )
            return redirect("accounts:user_register")
        form = VerifyCodeForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            expiration_time = code_instance.created + timedelta(minutes=2)
            is_valid_time = timezone.now() < expiration_time
            if cd["code"] == code_instance.code and is_valid_time:
                User.objects.create_user(phone_number=user_session["phone_number"],
                                         email=user_session["email"],
                                         full_name=user_session["full_name"],
                                         password=user_session["password"]
                                         )
                code_instance.delete()
                request.session.pop("user_registration_info", None)
                messages.success(request, "You registered", "success")
                return redirect("home:home")
            messages.error(request, "Invalid code", "danger")
            return redirect("accounts:verify_code")
        return render(request, "accounts/verify.html", {"form": form})
