from django import forms

class ParseForm(forms.Form):
    url = forms.URLField(
        label='URL статьи на eLibrary.ru',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.elibrary.ru/item.asp?id=...',
            'required': True
        }),
        help_text='Вставьте полную ссылку на статью'
    )