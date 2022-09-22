from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from itertools import chain
from django.http import HttpResponseNotFound
from django.contrib import messages
from django.db import IntegrityError

from . import forms, models
from authentication.models import User


@login_required
def home(request):
    tickets = models.Ticket.objects.filter(user__in=request.user.follows.all())
    reviews = models.Review.objects.filter(user__in=request.user.follows.all())
    tickets_and_reviews = sorted(chain(tickets, reviews), key=lambda instance: instance.time_created, reverse=True)

    paginator = Paginator(tickets_and_reviews, 6)
    page_numer = request.GET.get('page')
    page_obj = paginator.get_page(page_numer)
    context = {'page_obj': page_obj}
    return render(request, 'blog/home.html', context=context)


@login_required
def view_ticket(request, ticket_id):
    ticket = get_object_or_404(models.Ticket, id=ticket_id)
    return render(request, 'blog/view_ticket.html', {'ticket': ticket})

@login_required
def create_ticket(request):
    form = forms.TicketForm()
    if request.method == 'POST':
        form = forms.TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('home')
    return render(request, 'blog/create_ticket.html', context={'form': form})


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(models.Ticket, id=ticket_id)
    edit_form = forms.EditTicketForm(instance=ticket)
    delete_form = forms.DeleteTicketForm
    if request.method == 'POST':
        #if request.user == ticket.user à vérifier
        if 'edit_ticket' in request.POST:
            edit_form = forms.EditTicketForm(request.POST, instance=ticket)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('home')
        if 'delete_ticket' in request.POST:
            delete_form = forms.DeleteTicketForm(request.POST)
            if delete_form.is_valid():
                ticket.delete()
                return redirect('home')
        else:
            return HttpResponseNotFound('<h1>Page not found</h1>')
    context = {
        'edit_form': edit_form,
        'delete_form': delete_form,
    }
    return render(request, 'blog/edit_ticket.html', context=context)


@login_required
def view_review(request, review_id):
    review = get_object_or_404(models.Review, id=review_id)
    return render(request, 'blog/view_review.html', context={'review': review})


@login_required
def create_review(request, ticket_id):
    ticket = get_object_or_404(models.Ticket, id=ticket_id)
    review_form = forms.ReviewForm()
    if request.method == 'POST':
        review_form = forms.ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            models.Review.objects.create(
                ticket=ticket,
                user=request.user,
                headline=request.POST['headline'],
                rating=request.POST['rating'],
                body=request.POST['body']
            )
            ticket.review = True
            ticket.save()
            return redirect('home')
    return render(request, 'blog/create_review.html', context={'review_form': review_form, 'ticket': ticket})

@login_required
def create_review_without_ticket(request):
    review_form = forms.ReviewForm()
    ticket_form = forms.TicketForm()
    if request.method == 'POST':
        review_form = forms.ReviewForm(request.POST)
        ticket_form = forms.TicketForm(request.POST, request.FILES)
        if all([ticket_form.is_valid(), review_form.is_valid()]):
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            review = review_form.save(commit=False)
            models.Review.objects.create(
                ticket=ticket,
                user=request.user,
                headline=request.POST['headline'],
                rating=request.POST['rating'],
                body=request.POST['body']
            )
            return redirect('posts_feed')
    context = {
        'ticket_form': ticket_form,
        'review_form': review_form
    }
    return render(request, 'blog/create_review_without_ticket.html', context=context)


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(models.Review, id=review_id)
    edit_form = forms.EditReviewForm(instance=review)
    delete_form = forms.DeleteReviewForm()
    if request.method == 'POST':
        if 'edit_review' in request.POST:
            edit_form = forms.EditReviewForm(request.POST, instance=review)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('home')
        if 'delete_review' in request.POST:
            delete_form = forms.DeleteReviewForm(request.POST)
            if delete_form.is_valid():
                review.delete()
                return redirect('home')
        else:
            return HttpResponseNotFound('<h1>Page not found</h1>')
    context = {
        'edit_form': edit_form,
        'delete_form': delete_form,
    }
    return render(request, 'blog/edit_review.html', context=context)


def posts_feed(request):
    reviews = models.Review.objects.filter(user=request.user)
    tickets = models.Ticket.objects.filter(user=request.user)
    tickets_and_reviews = sorted(chain(tickets, reviews), key=lambda instance: instance.time_created, reverse=True)

    paginator = Paginator(tickets_and_reviews, 6)
    page_numer = request.GET.get('page')
    page_obj = paginator.get_page(page_numer)
    context = {'page_obj': page_obj}
    return render(request, 'blog/posts_feed.html', context=context)


@login_required
def follow_users(request):
    form = forms.FollowUsersForm()
    user_follows = models.UserFollows.objects.filter(user=request.user)
    followed_by = models.UserFollows.objects.filter(followed_user=request.user)
    if request.method == 'POST':
        form = forms.FollowUsersForm(request.POST)
        if form.is_valid():
            try:
                followed_user = User.objects.get(
                    username=request.POST['followed_user']
                )
                if request.user == followed_user:
                    messages.error(request, 'Vous ne pouvez pas vous suivre vous-même!')
                    return redirect('follow_users')
                else:
                    try:
                        models.UserFollows.objects.create(user=request.user, followed_user=followed_user)
                        messages.success(request, f"Vous êtes abonné maintenant à {followed_user}.")
                        return redirect('follow_users')
                    except IntegrityError:
                        messages.error(request, f'Vous êtes déjà adonné à {followed_user}.')
                        return redirect('follow_users')
            except User.DoesNotExist:
                messages.error(request, f' {form.data["followed_user"]} n\'existe pas.')
        else:
            form = forms.FollowUsersForm()

    context = {
        'form': form,
        'user_follows': user_follows,
        'followed_by': followed_by,
    }
    return render(request, 'blog/follow_users.html', context=context)


def delete_followed_user(request, user_id):
    follow = get_object_or_404(models.UserFollows, id=user_id)
    followed_user = follow.followed_user
    delete_form = forms.DeleteFollowedUser()
    if 'delete_follow' in request.POST:
        delete_form = forms.DeleteFollowedUser(request.POST)
        if delete_form.is_valid():
            follow.delete()
            return redirect('follow_users')
    context = {'delete_form': delete_form, 'followed_user': followed_user}
    return render(request, 'blog/delete_followed_user.html', context=context)
