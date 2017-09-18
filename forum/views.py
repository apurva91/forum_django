from __future__ import unicode_literals
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import login, authenticate
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse, Http404
from .models import ForumPost, PostCategory, Comment
from .forms import PostForm, SignUpForm, CommentForm#, #SearchForm
# Create your views here.

def SignUp(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.birth_date=form.cleaned_data.get('birth_date')
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'forum/signup.html', {'form': form})


def Index(request):
	latest_posts=ForumPost.objects.order_by('-date')
	paginator = Paginator(latest_posts, 5) # Show 25 contacts per page

	page = request.GET.get('page')
	try:
		latest_posts = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		latest_posts = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		latest_posts = paginator.page(paginator.num_pages)

	if request.user.is_authenticated:
	
		if request.method=='POST':
			form = PostForm(request.POST)
			if form.is_valid():
				post = form.save(commit=False)
				post.date = timezone.now()
				post.author = request.user
				post.save()
				return redirect('/posts/'+str(post.id))
		else:
			form = PostForm()
	else:
		form = 'blank'
	return render(request, 'forum/index.html', {'latest_posts':latest_posts, 'form':form})

def PostDetail(request,post_id):

	current_post = get_object_or_404(ForumPost, pk=post_id)
	current_post_comments = Comment.objects.filter(forumpost=current_post.id).order_by('-date')
	if request.user.is_authenticated:
		if request.method=='POST':
			form = CommentForm(request.POST)
			if form.is_valid():
				comment = form.save(commit=False)
				comment.date = timezone.now()
				comment.author = request.user
				comment.forumpost = current_post
				comment.save()
				return redirect('/posts/'+str(current_post.id))
		else:
			form = CommentForm()
	else:
		form='blank'
	return render(request,'forum/post_detail.html',{'current_post':current_post, 'current_post_comments':current_post_comments, 'form':form,})

def CategoryIndex(request, category):

	latest_posts_in_cat=ForumPost.objects.filter(category__url=category).order_by('-date')
	if latest_posts_in_cat.count()==0:
		raise Http404("Category Not Found")
	paginator = Paginator(latest_posts_in_cat, 5) # Show 25 contacts per page

	page = request.GET.get('page')
	try:
		latest_posts_in_cat = paginator.page(page)
	except PageNotAnInteger:
		latest_posts_in_cat = paginator.page(1)
	except EmptyPage:
		latest_posts_in_cat = paginator.page(paginator.num_pages)


	return render(request, 'forum/category_index.html', {'latest_posts_in_cat':latest_posts_in_cat})

def SearchForum(request):
	que = request.GET.get('q')
	query=ForumPost.objects.filter(Q(text__contains=que)|Q(topic__contains=que)).order_by('-date')
	paginator = Paginator(query, 5) # Show 25 contacts per page

	page = request.GET.get('page')
	try:
		query = paginator.page(page)
	except PageNotAnInteger:
		query = paginator.page(1)
	except EmptyPage:
		query = paginator.page(paginator.num_pages)

	return render(request,'forum/search.html',{'query':query, 'que':que})

def Profile(request,user):
	user_post=ForumPost.objects.filter(author__username=user).order_by('-date')[:5]
	user_data=User.objects.filter(username=user).get()
	return render(request, 'forum/profile.html', {'user_post':user_post,'user_data':user_data})
