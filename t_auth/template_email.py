import requests

from django.core.mail.backends.base import BaseEmailBackend
from trood_auth_client.authentication import get_service_token


class CustomEmailMassage:
    def __init__(self, to=None, link=None, template=None):
        if to:
            if isinstance(to, str):
                raise TypeError('"to" argument must be a list or tuple')
            self.to = list(to)
        else:
            self.to = []

        self.message_body = self.get_body(to, link, template)
        self.headers = {"Content-Type": "application/json",
                        "Authorization": get_service_token()}
        self.template = template

    def get_body(self, to, link, template):
        message_body = {
            "mailbox": 1,
            "to": to,
            "template": template,
            "data": {
                "link": link
            }
        }
        return message_body


class CustomEmailBackend(BaseEmailBackend):
    def __init__(self, mail_service):
        self.url = f"{mail_service}/api/v1.0/mails/from_template/"

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        num_sent = 0
        for email_message in email_messages:
            response = requests.post(self.url, json=email_message.message_body,
                                     headers=email_message.headers)                               
            response.raise_for_status()
            if response.status_code == 200:
                num_sent += 1
        return num_sent

