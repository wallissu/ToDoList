from django import forms
from .models import Todo

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = "__all__"
        widgets = {
            'duedate': forms.DateInput(attrs={
                'type': 'date',  # Gera o calendário no navegador
                'min': '2025-09-21'  # opcional: define data mínima (ex: hoje)
            })
        }