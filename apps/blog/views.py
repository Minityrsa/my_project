from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, TemplateView

from blog.forms import PostForm
from blog.models import Category, Post, Tag


class HomePageView(TemplateView):
    template_name = 'blog/pages/index.html'


class PostListView(ListView):
    queryset = Post.objects.filter(status="published")
    context_object_name = 'posts'
    template_name = 'blog/pages/post_list.html'


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


def tag_posts_view(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    # posts = Post.objects.filter(tags=tag, status='published')
    posts = tag.posts.filter(status='published')

    context = {
        'tag': tag,
        'posts': posts
    }
    return render(request, 'blog/pages/tag_posts.html', context)


def post_detail_view(request, post_slug):
    # Пост доступен, если он опубликован или если текущий пользователь является его автором
    if request.user.is_authenticated:
        condition = Q(slug=post_slug) & (Q(status="published") | Q(author=request.user))
    else:
        condition = Q(slug=post_slug) & Q(status="published")

    # post = Post.objects.get(condition)
    post = get_object_or_404(Post, condition)
    return render(request, 'blog/pages/post_detail.html', {'post': post})


@login_required
def post_add_view(request):
    form = PostForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            tag_names = form.cleaned_data.get('tags_input')

            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)

            return redirect('blog:post_detail', post_slug=post.slug)

    return render(
        request,
        'blog/pages/post_form.html',
        {
            "form": form,
            "title": "Добавить пост",
            "h1": "Новый пост",
            "submit_button_text": "Добавить",
        }
    )


def post_edit_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return render(request, 'blog/pages/not_allowed.html')

    extra_context = {
        "title": "Редактировать пост",
        "h1": "Редактирование",
        "submit_button_text": "Сохранить",
    }

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            form.save()

            post.tags.clear()
            tag_names = form.cleaned_data.get('tags_input')
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)

            return redirect("blog:post_detail", post_slug=post.slug)
        return render(
            request,
            'blog/pages/post_form.html',
            context={
                "form": form,
                **extra_context,
            }
        )

    existing_tags = ", ".join(tag.name for tag in post.tags.all())
    form = PostForm(instance=post, initial={'tags_input': existing_tags})
    return render(
        request,
        'blog/pages/post_form.html',
        context={
            "form": form,
            **extra_context,
        }
    )


def post_remove_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return render(request, 'blog/pages/not_allowed.html')

    if request.method == "POST":
        post.delete()
        return redirect("blog:post_list")

    return render(request, 'blog/pages/post_remove_confirm.html', {'post': post})