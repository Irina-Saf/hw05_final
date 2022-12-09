from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow

VISIBLE_POSTCOUNT: int = 10


@cache_page(20)
def index(request):
    posts = Post.objects.all().order_by('-pub_date')
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

    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user__exact=request.user, author__exact=author
        ).exists()

    else:
        following = False

    context = {
        'author': author,
        'page_obj': page_obj,
        "following": following,

    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post_id__exact=post.pk)
    context = {
        'post': post,
        "form": CommentForm(),
        "comments": comments,

    }
    template = 'posts/post_detail.html'

    return render(request, template, context)


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
    follower_user = request.user
    following_authors = Follow.objects.filter(
        user=follower_user).values("author")
    posts = Post.objects.filter(author__in=following_authors)

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
        if Follow.objects.get_or_create(user=following_user, author=author):
            return redirect("posts:profile", username=username)
    else:
        return redirect("posts:index")


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if Follow.objects.filter(user=user, author=author).exists():
        Follow.objects.filter(user=user, author=author).delete()
        return redirect("posts:profile", username=username)
    else:
        return redirect("posts:profile", username=username)
