from django import forms

from .models import Item

class ModelFormWithFileField(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['file']
