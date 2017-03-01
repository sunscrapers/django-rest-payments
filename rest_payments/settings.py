"""
REST Payments settings are stored under `REST_PAYMENTS` namespace.
Example of `settings.py` snippet to enable DRP:

REST_PAYMENTS = {
    'DEFAULT_INTEGRATION_CLASSES': (
        'rest_payments.integrations.StripeIntegration',
    ),
    'STRIPE_API_KEY': 'YOUR-STRIPE-SECRET-API-KEY',
}

This module exposes `drp_settings` object, which is based on DRF concept
that allows user to provide own configuration or otherwise use default
fallback value.

Keep in mind that you should NEVER commit your API keys into repository.
It's good idea to store such credentials somewhere inside deployment pipeline.
"""
import importlib

from django.conf import settings


DEFAULTS = {
    'DEFAULT_INTEGRATION_CLASSES': (),
    'PAYPAL_API_KEY': None,
    'STRIPE_API_KEY': None,

    'INTEGRATIONS_AUTO_FALLBACK': True,
    'REGISTER_MODEL_ADMINS': False,
    'UNEXPECTED_ERRORS_HANDLER': None,
}

IMPORT_SETTING_NAMES = (
    'DEFAULT_INTEGRATION_CLASSES',
)


def import_from_string(value, attr):
    try:
        parts = value.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        msg = "Could not import '%s' for setting '%s'. %s: %s." % (
            value, attr, e.__class__.__name__, e
        )
        raise ImportError(msg)


def perform_import(value, attr):
    if value is None:
        return None
    elif isinstance(value, (list, tuple)):
        return type(value)(import_from_string(item, attr) for item in value)
    return value


class PaymentSettings:
    def __init__(self):
        self.user_settings = getattr(settings, 'REST_PAYMENTS', {})

    def __getattr__(self, attr):
        if attr not in DEFAULTS:
            raise AttributeError('Invalid setting: {}'.format(attr))

        try:
            value = self.user_settings[attr]
        except KeyError:
            value = DEFAULTS[attr]

        if attr in IMPORT_SETTING_NAMES:
            value = perform_import(value, attr)

        setattr(self, attr, value)
        return value


drp_settings = PaymentSettings()
