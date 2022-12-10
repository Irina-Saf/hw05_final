from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

VISIBLE_POSTCOUNT: int = 10


def index(request):
    posts = Post.objects.all()
    page_obj = paginator_page_obj(posts, request)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator_page_obj(posts, request)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginator_page_obj(posts, request)

    following = request.user.is_authenticated and request.user.follower.filter(
        author=author).exists()

    context = {
        'author': author,
        'page_obj': page_obj,
        "following": following,

    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    comments = post.comments.all()
    context = {
        'post': post,
        "form": CommentForm(),
        "comments": comments,

    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)

    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'posts/create.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create.html', context)


def paginator_page_obj(posts, request):
    paginator = Paginator(posts, VISIBLE_POSTCOUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@login_required
def add_comment(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)

    page_obj = paginator_page_obj(posts, request)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    following_user = request.user

    if author != following_user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )

    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user

    Follow.objects.filter(user=user, author=author).delete()

    return redirect("posts:profile", username=username)
