from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView
)

from blog.forms import PostForm
from blog.models import Category, Post, Tag


class HomePageView(TemplateView):
    template_name = 'blog/pages/index.html'


class PostListView(ListView):
    queryset = Post.objects.filter(status="published")
    context_object_name = 'posts'
    template_name = 'blog/pages/post_list.html'
    paginate_by = 3


class CategoryPostsView(ListView):
    context_object_name = 'posts'
    template_name = 'blog/pages/category_posts.html'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        # return Post.objects.filter(category=self.category, status='published')
        return self.category.posts.filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagPostsView(ListView):
    context_object_name = 'posts'
    template_name = 'blog/pages/tag_posts.html'

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        # return Post.objects.filter(tags=self.tag, status='published')
        return self.tag.posts.filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class PostDetailView(DetailView):
    # model = Post # Необязательно
    slug_url_kwarg = 'post_slug'
    template_name = 'blog/pages/post_detail.html'
    # context_object_name = 'post' # Необязательно
    # slug_field = 'slug' # Необязательно

    def get_queryset(self):
        # Пост доступен, если он опубликован или если текущий пользователь является его автором
        if self.request.user.is_authenticated:
            return Post.objects.filter(
                Q(status="published") | Q(author=self.request.user)
            )
        return Post.objects.filter(status="published")

    def get_object(self, queryset=None):
        post = super().get_object(queryset)

        user = self.request.user
        session_key = f'post_{post.id}_viewed' # "post_62_viewed"
        if not self.request.session.get(session_key, False) and post.author != user:
            Post.objects.filter(id=post.id).update(views=F("views") + 1)
            post.views += 1
            self.request.session[session_key] = True

        if user.is_authenticated and user != post.author:
            post.viewed_by_users.add(user) # Дубликатов записей не будет

        return post


class PostAddView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    extra_context = {
        "title": "Добавить пост",
        "h1": "Новый пост",
        "submit_button_text": "Добавить"
    }
    template_name = 'blog/pages/post_form.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()

        tag_names = form.cleaned_data.get('tags_input')

        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag)

        return redirect('blog:post_detail', post_slug=post.slug)


class PostEditView(UpdateView):
    model = Post
    pk_url_kwarg = 'post_id' # - потому что в url <int:post_id>, а не <int:pk>
    form_class = PostForm
    template_name = 'blog/pages/post_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Получаем объект сразу и сохраняем в self.object
        self.object = self.get_object()

        # Проверяем автора
        if request.user != self.object.author:
            return render(request, 'blog/pages/not_allowed.html')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = "Редактировать пост"
        context['h1'] = "Редактирование"
        context['submit_button_text'] = "Сохранить"
        context['form'].fields['tags_input'].initial = ", ".join(tag.name for tag in self.object.tags.all())

        return context

    def form_valid(self, form):
        form.save()

        self.object.tags.clear()
        tag_names = form.cleaned_data.get('tags_input')
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            self.object.tags.add(tag)

        return redirect('blog:post_detail', post_slug=self.object.slug)


class PostRemoveView(DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/pages/post_remove_confirm.html'
    # context_object_name = 'post' # Необязательно
    success_url = reverse_lazy('blog:post_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.user != self.object.author:
            return render(request, 'blog/pages/not_allowed.html')

        return super().dispatch(request, *args, **kwargs)