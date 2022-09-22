from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.urls import path

import authentication.views, blog.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(
            template_name='authentication/login.html',
            redirect_authenticated_user=True),
         name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', PasswordChangeView.as_view(
        template_name='authentication/password_change_form.html'),
         name='password_change'),
    path('change-password-done/', PasswordChangeDoneView.as_view(
        template_name='authentication/password_change_done.html'),
         name='password_change_done'),
    path('home/', blog.views.home, name='home'),
    path('signup/', authentication.views.signup_page, name='signup'),
    path('follow-users/', blog.views.follow_users, name='follow_users'),
    path('follow-user/delete-followed-user/<int:user_id>/', blog.views.delete_followed_user, name='delete_followed_user'),
    path('follow-user/confirm_unsub/<int:user_id>/', blog.views.delete_followed_user, name='confirm_unsub'),
    path('ticket/<int:ticket_id>/', blog.views.view_ticket, name='view_ticket'),
    path('ticket/create/', blog.views.create_ticket, name='create_ticket'),
    path('ticket/<int:ticket_id>/edit/', blog.views.edit_ticket, name='edit_ticket'),
    path('review/<int:review_id>/', blog.views.view_review, name='view_review'),
    path('review/create/review-without-ticket/', blog.views.create_review_without_ticket, name='create_review_without_ticket'),
    path('review/create/<int:ticket>/', blog.views.create_review, name='create_review'),
    path('review/<int:review_id>/edit/', blog.views.edit_review, name='edit_review'),
    path('posts/', blog.views.posts_feed, name='posts_feed')

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)