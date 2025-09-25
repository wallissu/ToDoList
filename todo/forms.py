from django import forms
from .models import Todo
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class TodoForm(forms.ModelForm):

    class Meta:
        model = Todo
        fields = ['title', 'details', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'details': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Task Details'}),
            'title': forms.TextInput(attrs={'placeholder': 'Task Title'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar o campo due_date opcional
        self.fields['due_date'].required = False    

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    