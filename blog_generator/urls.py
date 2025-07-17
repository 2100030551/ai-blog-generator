from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),  # Home page with video input
    path('generate/', views.generate_blog_view, name='generate'),  # POST triggers blog generation
    path('blogs/', views.all_blogs_view, name='all_blogs'),  # List of all blogs for user
    path('blogs/<int:id>/', views.blog_detail_view, name='blog_detail'),  # Detail of single blog post
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='signup'),
]
