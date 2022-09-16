from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DeleteView
from django.core.paginator import Paginator
from itertools import chain
from django.http import HttpResponseNotFound
from django.contrib import messages
from django.db import IntegrityError
from . import forms, models
from authentication.models import User
from django.contrib.auth.models import User

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
    form = forms.TicketForm(request.POST, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('home')
    return render(request, 'blog/create_ticket.html', context={'form': form})


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(models.Ticket, id=ticket_id)
    edit_form = forms.TicketForm(instance=ticket)
    delete_form = forms.DeleteTicketForm
    if request.method == 'POST':
        if 'edit_ticket' in request.POST:
            edit_form = forms.TicketForm(request.POST, instance=ticket)
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
def create_review(request, ticket):
    numbers_tickets = models.Review.objects.filter(ticket=ticket)
    review_form = forms.ReviewForm()
    if request.method == 'POST':
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('home')
    return render(request, 'blog/create_review.html', context={'review_form': review_form})

@login_required
def create_review_without_ticket(request):
    ticket_form = forms.TicketForm(request.POST, request.FILES)
    review_form = forms.ReviewForm(request.POST)
    if request.method == 'POST':
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
    edit_form = forms.ReviewForm(instance=review)
    delete_form = forms.DeleteReviewForm()
    if request.method == 'POST':
        if 'edit_review' in request.POST:
            edit_form = forms.ReviewForm(request.POST, instance=review)
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


@login_required
def follow_users(request):
    if request.method == 'POST':
        form = forms.FollowUsersForm(request.POST, instance=request.user)
        if form.is_valid():
            try:
                followed_user = User.objects.get(username=request.POST['followed_user'])
                if request.user == followed_user:
                    messages.error(request, f"Vous ne pouvez pas vous abonner à vous même")
                else:
                    try:
                        models.UserFollows.objects.create(user=request.user, followed_user=followed_user)
                        messages.success(request, f"Vous êtes abonner à {followed_user}.")
                    except IntegrityError:
                        messages.error(request, f"Vous êtes déjà abonner à cet utilisateur")
            except User.DoesNotExist:
                messages.error(request, f"Cet utilisateur n'existe pas")
        else:
            messages.error(request, f"l'utilisateur n'existe pas.")
    else:
        form = forms.FollowUsersForm()

    user_follows = models.UserFollows.objects.filter(user=request.user).order_by('followed_user')
    followed_by = models.UserFollows.objects.filter(followed_user=request.user).order_by('user')

    context = {
        'form': form,
        'user_follows': user_follows,
        'followed_by' : followed_by,

    }

    return render(request, 'blog/follow_users_form.html', context=context)


def posts_feed(request):
    reviews = models.Review.objects.filter(user=request.user)
    tickets = models.Ticket.objects.filter(user=request.user)
    tickets_and_reviews = sorted(chain(tickets, reviews), key=lambda instance: instance.time_created, reverse=True)

    paginator = Paginator(tickets_and_reviews, 6)
    page_numer = request.GET.get('page')
    page_obj = paginator.get_page(page_numer)
    context = {'page_obj': page_obj}
    return render(request, 'blog/posts_feed.html', context=context)


class UnsubscribeView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = models.UserFollows
    success_url = 'follow-users/'
    context_object_name = 'unsub'

    def test_func(self):
        unsub = self.get_object()
        if self.request.user == unsub.user:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, f'Vous avez cessé de suivre {self.get_object().followed_user}.')
        return super(UnsubscribeView, self).delete(request, *args, **kwargs)