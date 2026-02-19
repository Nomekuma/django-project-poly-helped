from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("members/", views.members, name="members"),
    path("contact/", views.contact, name="contact"),
    path("register/", views.register, name="register"),
    path("forum/", views.forum, name="forum"),
    path("topic/<int:pk>/", views.topic_detail, name="topic_detail"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
