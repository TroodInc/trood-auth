import requests
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from trood.contrib.django.mail.backends import TroodEmailMessageTemplate


def send_registration_mail(data):
    if settings.MAILER_TYPE == 'TROOD':
        message = TroodEmailMessageTemplate(to=[data['login']], template='ACCOUNT_REGISTERED', data=data)
        message.send()
    elif settings.MAILER_TYPE == 'SMTP':
        message_body = render_to_string('register.html', context=data)
        message = EmailMessage(
            to=[data['login']],
            subject=str(f'Wellcome to {settings.PROJECT_NAME}'),
            body=message_body
        )
        message.send()


def is_captcha_valid(captcha_key):
    return requests.post(settings.CAPTCHA_VALIDATION_SERVER, data={
        'secret': settings.CAPTCHA_SECRET_KEY,
        'response': captcha_key
    }, verify=True).json().get('success')
