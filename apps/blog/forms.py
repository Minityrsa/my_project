from django import forms

from blog.models import Post


class PostForm(forms.ModelForm):
  class Meta:
    model = Post
    fields = ['title', 'category', 'text', 'image']
    widgets = {
      'title': forms.TextInput(attrs={
        'placeholder': "Максимальная длина 200 символов"
      }),
      'text': forms.Textarea(attrs={
        'rows': 3,
        'cols': 20
      }),
      'category': forms.Select(attrs={'class': 'form-control'}),
      'image': forms.FileInput(attrs={'class': 'form-control'})
    }
    labels = {
      'title': 'Заголовок поста:',
      'text': 'Текст поста:',
      'category': 'Категория:',
      'image': 'Картинка поста'
    }
    help_texts = {
      'category': "- можно выбрать только одну категорию"
    }

  def clean_title(self):
    title = self.cleaned_data['title'].strip()

    if len(title) < 10:
      raise forms.ValidationError("Заголовок не должен быть короче 10 символов.")

    return title