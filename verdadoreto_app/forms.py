from django import forms
from .models import Pack, Action

class PackForm(forms.ModelForm):
    class Meta:
        model = Pack
        fields = ['name']  # el owner lo ponemos en la vista
        labels = {'name': 'Nombre del pack'}

class ActionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = ['text', 'active']
        labels = {
            'tipo': 'Tipo',
            'texto': 'Texto',
            'activa': 'Activa',
        }
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 4}),
        }
