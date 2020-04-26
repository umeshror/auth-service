from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    country_code = models.CharField('country code',
                                    max_length=3,
                                    help_text='Country code of the phone number')
    phone_number = models.CharField('phone number',
                                    db_index=True,
                                    max_length=15,
                                    help_text='Include the country code. for the phone number')


class OneTimePassCode(models.Model):
    code = models.CharField(max_length=255)
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)
    valid_until = models.DateTimeField()

    failure_timestamp = models.DateTimeField(
        null=True, blank=True,
        help_text="A timestamp of the last failed verification attempt."
                  "Null if last attempt succeeded."
    )
    failure_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of failed attempts."
    )

    def __unicode__(self):
        return self.user
