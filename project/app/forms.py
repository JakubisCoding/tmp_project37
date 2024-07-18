from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password




class TeacherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    username = forms.CharField()
    email = forms.CharField()



    class Meta:
        model = Teacher
        
        
        fields = ['username', 'email', 'subject', 'password']
# this adds new teacher
    def save(self):
        user = User.objects.create(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=make_password(self.cleaned_data['password'])
        )

        teacher = Teacher.objects.create(
            user=user,
            subject=self.cleaned_data['subject'],

        )

        return teacher