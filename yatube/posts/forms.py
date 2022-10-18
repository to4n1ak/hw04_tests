from django import forms
from .models import Post
from django.forms import ModelForm


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group',)
        labels = {
            'text': 'Текст поста',
            'group': 'Сообщество',
        }
        help_text = {
            'text': 'Заполните текст поста',
            'group': 'Выберите сообщество',
        }

    def clean_subject(self):
        data = self.cleaned_data['text']

        if data == '':
            raise forms.ValidationError('Пожалуйста, напишите пост')

        return data
