from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
    get_user_model,
)
from .forms import RegistrationForm, TopicForm, PostForm
from .models import Topic, Registration


def home(request):
    return render(request, "pages/home.html")


def about(request):
    return render(request, "pages/about.html")


def members(request):
    # Build member/contributor stats
    from .models import Post, Topic, Registration

    members = []
    for reg in Registration.objects.order_by("-created_at"):
        full_name = f"{reg.first_name} {reg.last_name}".strip()
        # count posts and topics matching either full name or email (case-insensitive)
        post_count = Post.objects.filter(author_name__iexact=full_name).count()
        if post_count == 0:
            post_count = Post.objects.filter(author_name__iexact=reg.email).count()

        topic_count = Topic.objects.filter(author_name__iexact=full_name).count()
        if topic_count == 0:
            topic_count = Topic.objects.filter(author_name__iexact=reg.email).count()

        members.append(
            {
                "name": full_name or reg.email,
                "email": reg.email,
                "joined": reg.created_at,
                "posts": post_count,
                "topics": topic_count,
                "contributions": post_count + topic_count,
            }
        )

    # sort members by contributions desc
    members_sorted = sorted(members, key=lambda m: m["contributions"], reverse=True)

    # top contributors (top 5)
    top_contributors = members_sorted[:5]

    return render(
        request,
        "pages/members.html",
        {"members": members_sorted, "top_contributors": top_contributors},
    )


def contact(request):
    return render(request, "pages/contact.html")


def register(request):
    # Clear any previous messages when showing the registration form
    # so old success/info messages don't appear on the register page.
    if request.method == "GET":
        # consume and discard existing messages
        list(messages.get_messages(request))

    if request.method == "POST":
        # Debug: print raw POST payload to help diagnose missing fields
        try:
            print("REGISTER POST DATA:", dict(request.POST))
        except Exception:
            print("REGISTER POST DATA: <unprintable>")
        form = RegistrationForm(request.POST)
        if form.is_valid():
            reg = form.save()
            # normalize email and create or get a Django User and login
            User = get_user_model()
            email_norm = (reg.email or "").strip().lower()
            user, created = User.objects.get_or_create(
                username=email_norm,
                defaults={
                    "email": email_norm,
                    "first_name": reg.first_name,
                    "last_name": reg.last_name,
                },
            )
            if created:
                # create_user with no password sets unusable password
                user.set_unusable_password()
                user.save()
            auth_login(request, user)
            messages.success(request, "Registration successful. You are logged in.")
            return redirect("forum")
        else:
            # Debug: surface form errors in logs and to the user messages
            try:
                err_json = form.errors.as_json()
            except Exception:
                err_json = str(form.errors)
            print("Registration form invalid:", err_json)
            # Add each field error to messages so it appears on the rendered HTML
            for field, errs in form.errors.items():
                for e in errs:
                    messages.error(request, f"{field}: {e}")
    else:
        form = RegistrationForm()

    # Build context; on GET explicitly clear messages so old notifications don't appear
    context = {"form": form}
    if request.method == "GET":
        # consume and discard any previous messages and pass an empty messages list
        list(messages.get_messages(request))
        context["messages"] = []

    return render(request, "pages/register.html", context)


def forum(request):
    topics = Topic.objects.order_by("-created_at")
    # handle new topic creation inline
    if request.method == "POST" and "create_topic" in request.POST:
        # require login
        if not request.user.is_authenticated:
            messages.error(
                request, "You must be registered and logged in to create topics."
            )
            return redirect("login")

        tform = TopicForm(request.POST)
        if tform.is_valid():
            topic = tform.save(commit=False)
            # set author name from auth user
            topic.author_name = (
                f"{request.user.first_name} {request.user.last_name}".strip()
                or request.user.email
            )
            topic.save()
            messages.success(request, "Topic created.")
            return redirect("forum")
    else:
        tform = TopicForm()
    # recent activity: last 5 posts
    from .models import Post

    recent_posts = Post.objects.order_by("-created_at")[:5]
    total_topics = Topic.objects.count()
    total_posts = Post.objects.count()
    active_members = Registration.objects.count()
    online_now = 1 if request.user.is_authenticated else 0

    return render(
        request,
        "pages/forum.html",
        {
            "topics": topics,
            "topic_form": tform,
            "recent_posts": recent_posts,
            "total_topics": total_topics,
            "total_posts": total_posts,
            "active_members": active_members,
            "online_now": online_now,
        },
    )


def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    posts = topic.posts.order_by("created_at")
    if request.method == "POST":
        # require login
        if not request.user.is_authenticated:
            messages.error(
                request, "You must be registered and logged in to post replies."
            )
            return redirect("login")

        pform = PostForm(request.POST)
        if pform.is_valid():
            post = pform.save(commit=False)
            post.topic = topic
            # set author name from auth user
            post.author_name = (
                f"{request.user.first_name} {request.user.last_name}".strip()
                or request.user.email
            )
            post.save()
            messages.success(request, "Reply posted.")
            return redirect("topic_detail", pk=pk)
    else:
        pform = PostForm()
    return render(
        request,
        "pages/topic_detail.html",
        {"topic": topic, "posts": posts, "post_form": pform},
    )


def login_view(request):
    # simple email-based login using Registration -> User
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        if not email:
            messages.error(request, "Please provide an email.")
            return redirect("login")
        try:
            User = get_user_model()
            user = User.objects.filter(username__iexact=email).first()
            if not user:
                # Fallback: try matching by the User.
                user = User.objects.filter(email__iexact=email).first()
            if not user:
                # Try to find a registration record and create a User from it
                reg = Registration.objects.filter(email__iexact=email).first()
                if reg:
                    user, created = User.objects.get_or_create(
                        username=email,
                        defaults={
                            "email": email,
                            "first_name": reg.first_name,
                            "last_name": reg.last_name,
                        },
                    )
                    if created:
                        user.set_unusable_password()
                        user.save()
                else:
                    messages.error(request, "No registration found with that email.")
                    return redirect("register")
            auth_login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("forum")
        except Exception:
            messages.error(request, "Login error.")
            return redirect("login")
    return render(request, "pages/login.html")


def logout_view(request):
    auth_logout(request)
    messages.success(request, "Logged out.")
    return redirect("home")
