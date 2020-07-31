from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class AuditMixin(models.Model):
    """
    AuditMixin is used for auditing purpose.
    By inheriting this model we can track who created
    the object at what time and who updated

    Apart from basic auditing it also captures historic data
    Which helps to store every create, update, or delete occurs operation.
    """
    created_by = models.ForeignKey('core.User',
                                   on_delete=models.PROTECT,
                                   related_name='+',
                                   help_text='User who created the object')

    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Time at which object was created')

    updated_by = models.ForeignKey('core.User',
                                   null=True,
                                   related_name='+',
                                   on_delete=models.PROTECT,
                                   help_text='User who updated the object')

    updated_at = models.DateTimeField(auto_now=True,
                                      null=True,
                                      help_text='Time at which object was updated')

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=30, blank=False, null=False)

    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)

    country_code = models.CharField(_('country code'),
                                    blank=True,
                                    max_length=3,
                                    help_text='Country code of the phone number')
    phone_number = models.CharField(_('phone number'),
                                    db_index=True,
                                    blank=True,
                                    max_length=15,
                                    help_text='Include the country code. for the phone number')

    profile_picture_url = models.URLField(blank=True, null=True, help_text='User profile picture url')

    history = HistoricalRecords()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        """
        Before saving change the username,
        """
        self.username = self.email
        super(User, self).save(*args, **kwargs)


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
