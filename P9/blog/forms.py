from django import forms
from django.contrib.auth import get_user_model
from . import models


class TicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ['title', 'description', 'image']


class EditTicketForm(forms.ModelForm):
    edit_ticket = forms.BooleanField(widget=forms.HiddenInput, initial=True)
    class Meta:
        model = models.Ticket
        fields = ['title', 'description', 'image']


class DeleteTicketForm(forms.Form):
    delete_ticket = forms.BooleanField(widget=forms.HiddenInput, initial=True)


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        initial=1,
        label="Rating",
        widget=forms.RadioSelect(),
        choices=((1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"))
    )
    class Meta:
        model = models.Review
        fields = ['headline', 'rating', 'body']

class EditReviewForm(forms.ModelForm):
    edit_review = forms.BooleanField(widget=forms.HiddenInput, initial=True)
    class Meta:
        model = models.Review
        fields = ['headline', 'rating', 'body']

class DeleteReviewForm(forms.Form):
    delete_review = forms.BooleanField(widget=forms.HiddenInput, initial=True)

User = get_user_model()

class FollowUsersForm(forms.Form):
    followed_user = forms.CharField(label=False, widget=forms.TextInput())


class DeleteFollowedUser(forms.Form):
    delete_follow = forms.BooleanField(widget=forms.HiddenInput, initial=True)
