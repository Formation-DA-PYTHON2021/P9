from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator
from itertools import chain
from django.http import HttpResponseNotFound

from . import forms, models



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
            review.user = request.user
            review.save()
            return redirect('home')
    return render(request, 'blog/create_review.html', context={'review_form': review_form, 'ticket': ticket})

@login_required
def create_review_without_ticket(request):
    ticket_form = forms.TicketForm()
    review_form = forms.ReviewForm()
    if request.method == 'POST':
        review_form = forms.ReviewForm(request.POST)
        ticket_form = forms.TicketForm(request.POST, request.FILES)
        if all([ticket_form.is_valid(), review_form.is_valid()]):
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            review = review_form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('home')
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
    form = forms.FollowUsersForm(request.POST, instance=request.user)
    user_follows = models.UserFollows.objects.filter(user=request.user)
    followed_by = models.UserFollows.objects.filter(followed_user=request.user)
    if request.method == 'POST':
        form = forms.FollowUsersForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {
        'form': form,
        'user_follows': user_follows,
        'followed_by': followed_by,
    }
    return render(request, 'blog/follow_users.html', context=context)


def delete_followed_user(request, user_id):
    followed_user = get_object_or_404(models.UserFollows, id=user_id)
    delete_form = forms.DeleteFollowedUser()
    if request.method == 'POST':
        delete_form = forms.DeleteFollowedUser(request.POST)
        if delete_form.is_valid():
            followed_user.delete()
            return redirect('home')
    context = {'delete_form': delete_form}
    return render(request, 'blog/follow_users.html', context=context)
