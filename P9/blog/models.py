from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    review = models.BooleanField(default=False)
    IMAGE_MAX_SIZE = (800, 800)

    if image is True:
        def resize_image(self):
            image = Image.open(self.image)
            image.thumbnail(self.IMAGE_MAX_SIZE)
            image.save(self.image.path)

        def save(self, *args, **kwargs):
            super().save(*args, **kwargs)
            self.resize_image()

    def __str__(self):
        return f'{self.title}, écrit part {self.user}, le {self.time_created}'

class Review(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=True, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[
        MinValueValidator(0), MaxValueValidator(5)])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.headline


class UserFollows(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed_by')
    class Meta :
        unique_together = ('user', 'followed_user')

