from django.contrib.auth.forms import UserCreationForm
from django.forms import fields
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = "__all__"