from django import forms


class PostForm(forms.Form):
  title = forms.CharField(
    max_length=200,
    label="Заголовок поста:",
    widget=forms.TextInput(attrs={
      'placeholder': "Максимальная длина 200 символов"
    }) # Можно передавать другие атрибуты, например, "class": 'title-input'
  ) # Можно указать: required=False

  text = forms.CharField(
    label="Текст поста:",
    widget=forms.Textarea(attrs={
      'rows': 3,
      'cols': 20
    })
  )

  def clean_title(self):
    title = self.cleaned_data['title'].strip()

    if len(title) < 10:
      raise forms.ValidationError("Заголовок не должен быть короче 10 символов.")

    return title