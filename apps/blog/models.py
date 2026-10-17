from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
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
    tags = models.ManyToManyField("Tag", related_name='posts', blank=True, verbose_name='Теги')
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

    def get_absolute_url(self):
        # return f"/posts/{self.slug}/"
        # return reverse('blog:post_detail', args=[self.slug])
        return reverse('blog:post_detail', kwargs={'post_slug': self.slug})

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

    def get_absolute_url(self):
        return reverse('blog:category_posts', kwargs={'category_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, editable=False)

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"
        # db_table = "blog_tags"

    def get_absolute_url(self):
        return reverse('blog:tag_posts', kwargs={'tag_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return f'#{self.name}'