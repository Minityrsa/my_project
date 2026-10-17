from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode

User = get_user_model()


class Post(models.Model):
    STATUS_CHOICES = (
        ('published', 'Опубликован'),
        ('draft', 'Черновик')
    )

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, editable=False)
    category = models.ForeignKey(
        'Category',
        related_name='posts',
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE, # Можно указать SET_NULL
        related_name='posts'
    )
    status = models.CharField(choices=STATUS_CHOICES, default='draft', verbose_name="Статус")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'
        # db_table = 'blog_posts'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, editable=False)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = "категории"
        # db_table = "blog_categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name