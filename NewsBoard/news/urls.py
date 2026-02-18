from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

app_name = "news"

urlpatterns = [
    path('', PostList.as_view(), name='post_list'),
    path('post/<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('post/create/', PostCreate.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', PostUpdate.as_view(), name='post_edit'),

    path('comments/', MyCommentsList.as_view(), name='my_comments'),
    path('post/<int:pk>/comment/', CommentCreate.as_view(), name='comment_create'),
    path('comments/<int:pk>/accept/', accept_comment, name='comment_accept'),
    path('comments/<int:pk>/delete/', delete_comment, name='comment_delete'),

    path('register/', register_view, name='register'),
    path('confirm-email/', confirm_email_view, name='confirm_email'),
    path('login/', auth_views.LoginView.as_view(template_name='posts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]