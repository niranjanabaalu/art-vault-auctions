from django import forms
from .models import Painting
from django.contrib.auth.forms import UserCreationForm
#from .models import CustomUser

from django import forms
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Passwords do not match.")

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    
class PaintingForm(forms.ModelForm):
    class Meta:
        model = Painting
        exclude = ['notified', 'sold', 'winner', 'price_range', 'status', 'user']
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe the painting, its inspiration, and details...','class': 'form-control'}),
            'price_range': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'current_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={'placeholder': 'Mention any additional information, such as medium, size, or artist notes...','class': 'form-control'}),
        }

from django import forms
from .models import Profile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

