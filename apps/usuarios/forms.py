from django import forms
from .models import Usuario

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['avatar']