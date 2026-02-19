from django.db import models


class Registration(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    cohort = models.CharField(max_length=100, blank=True)
    campus = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    motivation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"


class Topic(models.Model):
    CATEGORY_CHOICES = [
        ("general", "General Discussion"),
        ("tech", "Technical Help"),
        ("study", "Study Groups"),
        ("games", "Game Development"),
        ("security", "Cybersecurity"),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="general"
    )
    author_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    topic = models.ForeignKey(Topic, related_name="posts", on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.author_name} on {self.topic_id}"
