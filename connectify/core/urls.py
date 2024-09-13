from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/edit/delete_avatar/', views.delete_avatar, name='delete_avatar'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('signup/', views.signup, name='signup'),
    path('upload/', views.upload, name='upload'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('follow-user/', views.follow_user, name='follow_user'),
    path('unfollow-user/', views.unfollow_user, name='unfollow_user'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('check_follow_status/', views.check_follow_status, name='check_follow_status'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
