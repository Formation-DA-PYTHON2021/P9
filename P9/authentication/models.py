from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    CREATOR = 'CREATOR'
    SUBSCRIBER = 'SUBSCRIBER'

    ROLE_CHOISES = (
        (CREATOR, 'Créateur'),
        (SUBSCRIBER, 'Abonné')
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOISES, verbose_name='Rôle')

    follows = models.ManyToManyField(
        'self',
        limit_choices_to={'role': CREATOR},
        symmetrical=False,
        verbose_name='suit',
    )