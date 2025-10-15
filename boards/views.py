from django.shortcuts import render, get_object_or_404, redirect
from .models import Board, Topic, Post
from django.contrib.auth.decorators import login_required
from .forms import NewTopicForm
from django.contrib.auth.views import LogoutView
from .forms import PostForm
from django.db.models import Count
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class CustomLogoutView(LogoutView):
    http_method_names = ["get", "post"]  # allow both GET and POST


class BoardListView(ListView):
    model = Board
    context_object_name = "boards"
    template_name = "home.html"


class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "topic_posts.html"
    paginate_by = 2

    def get_context_data(self, **kwargs):
        self.topic.views += 1
        self.topic.save()
        kwargs["topic"] = self.topic
        kwargs["board"] = self.topic.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(
            Topic, board__pk=self.kwargs.get("pk"), pk=self.kwargs.get("topic_pk")
        )
        queryset = self.topic.posts.order_by("created_at")
        return queryset


class TopicListView(ListView):
    model = Topic
    context_object_name = "topics"
    template_name = "topics.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs["board"] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get("pk"))
        queryset = self.board.topics.order_by("-last_updated").annotate(
            replies=Count("posts") - 1
        )
        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = request.user  # currently logged-in user

    if request.method == "POST":
        form = NewTopicForm(request.POST)
        if form.is_valid():
            # Create topic but don't save yet
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()

            # Create the first post
            Post.objects.create(
                message=form.cleaned_data.get("message"),
                topic=topic,
                created_by=request.user,
            )

            # Redirect to the topic page (or posts page)
            return redirect("topic_posts", pk=board.pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()

    return render(request, "new_topic.html", {"board": board, "form": form})


def topic_posts(request, pk, topic_pk):
    board = get_object_or_404(Board, pk=pk)
    topic = get_object_or_404(Topic, pk=topic_pk, board=board)
    topic.views += 1
    topic.save()
    return render(
        request,
        "topic_posts.html",
        {
            "board": board,
            "topic": topic,
        },
    )


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            topic.last_updated = timezone.now()  # <- here
            topic.save()
            return redirect("topic_posts", pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, "reply_topic.html", {"topic": topic, "form": form})


@method_decorator(login_required, name="dispatch")
class PostUpdateView(UpdateView):
    model = Post
    fields = ("message",)
    template_name = "edit_post.html"
    pk_url_kwarg = "post_pk"
    context_object_name = "post"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect("topic_posts", pk=post.topic.board.pk, topic_pk=post.topic.pk)
