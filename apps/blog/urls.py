from django.urls import path

from . import views

# from blog.views import home_page_view
# from .views import home_page_view

app_name = 'blog'

urlpatterns = [
    path('', views.home_page_view, name="home_page"),
    path('posts/', views.post_list_view, name="post_list"),
]
