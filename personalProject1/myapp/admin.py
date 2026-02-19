from django.contrib import admin
from .models import Registration, Topic, Post


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "cohort",
        "campus",
        "created_at",
    )
    search_fields = ("first_name", "last_name", "email", "cohort", "campus")


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author_name", "created_at")
    list_filter = ("category",)
    search_fields = ("title", "author_name")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("topic", "author_name", "created_at")
    search_fields = ("author_name", "content")


from django.contrib import admin

# Register your models here.
