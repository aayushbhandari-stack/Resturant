from django import forms
from .models import Food


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = [
            "name",
            "price",
            "category",
            "image",
            "is_available",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter food name",
            }),

            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter price",
                "step": "0.01",
            }),

            "category": forms.Select(attrs={
                "class": "form-control",
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": ".jpg,.jpeg,.png,.webp",
            }),

            "is_available": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }
