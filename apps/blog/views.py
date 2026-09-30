from django.shortcuts import render

from blog.models import Post


def home_page_view(request):
    return render(request, template_name='blog/index.html')


def post_list_view(request):
    posts = Post.objects.all()
    return render(request, template_name='blog/post_list.html', context={'posts': posts})