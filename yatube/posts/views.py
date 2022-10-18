from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm
from .utils import page_num
from django.contrib.auth.decorators import login_required

POST_PER_PAGE = 10  # Кол-во постов на странице


def index(request):
    post_list = Post.objects.select_related('group')
    page_obj = page_num(request, post_list, POST_PER_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('group')
    page_obj = page_num(request, post_list, POST_PER_PAGE)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = page_num(request, post_list, POST_PER_PAGE)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        data=request.POST or None,
    )

    if request.method != 'POST' or not form.is_valid():
        context = {'form': form, 'is_edit': False}
        return render(request, 'posts/create_post.html', context)

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post.id)

    form = PostForm(
        data=request.POST or None,
        instance=post,
    )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)

    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    template = 'posts/create_post.html'
    return render(request, template, context)
