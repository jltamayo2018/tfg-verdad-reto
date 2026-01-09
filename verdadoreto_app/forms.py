from django import forms
from .models import Pack, Action, PackCollaborator
from django.contrib.auth.models import User

class PackForm(forms.ModelForm):
    LEVEL_CHOICES = [
        (1, "1 - Suave"),
        (2, "2 - Tranquilo"),
        (3, "3 - Medio"),
        (4, "4 - Duro"),
        (5, "5 - Extremo"),
    ]

    level = forms.ChoiceField(choices=LEVEL_CHOICES)

    class Meta:
        model = Pack
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
            'level': forms.Select(attrs={
                'class': 'select-level',
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

class AddCollaboratorForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario", max_length=150)
    role = forms.ChoiceField(choices=PackCollaborator.ROLE_CHOICES, initial=PackCollaborator.EDITOR)

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Ese usuario no existe.")
        cleaned['target_user'] = user
        return cleaned