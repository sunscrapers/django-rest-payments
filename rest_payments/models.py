from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _


class Customer(models.Model):
    user = models.OneToOneField(
        on_delete=models.CASCADE,
        primary_key=True,
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('customer'),
    )


class Source(models.Model):
    pass


class Charge(models.Model):
    CHARGE_STATUS_FAILED = 0
    CHARGE_STATUS_PENDING = 1
    CHARGE_STATUS_SUCCEEDED = 2
    CHARGE_STATUS_CHOICES = (
        (CHARGE_STATUS_FAILED, _('failed')),
        (CHARGE_STATUS_PENDING, _('pending')),
        (CHARGE_STATUS_SUCCEEDED, _('succeeded')),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
    )

    status = models.PositiveSmallIntegerField(
        choices=CHARGE_STATUS_CHOICES,
        editable=False,
        verbose_name=_('status'),
    )

    amount = models.PositiveIntegerField(
        editable=False,
        verbose_name=_('amount'),
    )

    # ISO-4217 currency code
    currency = models.CharField(
        editable=False,
        max_length=16,
        verbose_name=_('currency'),
    )

    integration_id = models.TextField(
        editable=False,
        verbose_name=_('integration id'),
    )

    @property
    def is_completed(self):
        return self.status is not self.CHARGE_STATUS_PENDING

    def get_total_refunds_amount(self):
        return self.refunds.all().aggregate(Sum('amount'))['amount__sum']

    def __str__(self):
        return 'Charge - {} {} @{}'.format(
            int(self.amount) / 100.0,
            self.currency,
            self.created_at
        )


class Refund(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
    )

    charge = models.ForeignKey(
        editable=False,
        on_delete=models.CASCADE,
        related_name='refunds',
        to=Charge,
        verbose_name=_('refund'),
    )

    amount = models.PositiveIntegerField(
        editable=False,
        verbose_name=_('amount'),
    )

    # ISO-4217 currency code
    currency = models.CharField(
        editable=False,
        max_length=16,
        verbose_name=_('currency'),
    )

    def __str__(self):
        return ''
