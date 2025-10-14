from django import forms
from .models import Pack, Action

class PackForm(forms.ModelForm):
    class Meta:
        model = Pack
        # añadimos los nuevos campos
        fields = ['name', 'category', 'level']  # el owner se asigna en la vista
        labels = {
            'name': 'Nombre del pack',
            'category': 'Categoría',
            'level': 'Nivel (1 a 5)',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Introduce un nombre para tu pack',
            }),
            'category': forms.Select(attrs={
                'class': 'select-category',
            }),
            'level': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'step': 1,
                'class': 'input-level',
            }),
        }
        help_texts = {
            'level': 'Indica el nivel de picantez o dificultad (1 = suave, 5 = extremo).'
        }


class ActionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = ['text', 'active']
        labels = {
            'text': 'Texto',
            'active': 'Activa',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }
