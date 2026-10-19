from django.urls import path

from . import views
# Можно так:
# from blog.views import home_page_view
# from .views import home_page_view

app_name = 'blog'

urlpatterns = [
    path('', views.HomePageView.as_view(), name="home_page"),
    path('posts/', views.PostListView.as_view(), name="post_list"),
    path('posts/category/<slug:category_slug>/', views.CategoryPostsView.as_view(), name="category_posts"),
    path('posts/tag/<slug:tag_slug>/', views.TagPostsView.as_view(), name="tag_posts"),
    path('posts/add/', views.post_add_view, name='post_add'),
    path('posts/<slug:post_slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit_view, name="post_edit"),
    path('posts/<int:post_id>/remove/', views.post_remove_view, name="post_remove"),
]