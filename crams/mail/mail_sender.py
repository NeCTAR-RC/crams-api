# coding=utf-8
"""
Mail Sender methods
"""

from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMessage

__author__ = 'simonyu'


def send_notification(
        sender,
        subject,
        mail_content,
        template_name,
        recipient_list,
        cc_list,
        bcc_list,
        reply_to=None):
    """
    send notification
    :param sender:
    :param subject:
    :param mail_content:
    :param template_name:
    :param recipient_list:
    :param cc_list:
    :param bcc_list:
    :param reply_to:
    """
    template = get_template(template_name)
    ctx = Context({'request': mail_content})
    message = template.render(ctx)
    email = EmailMessage(subject=subject, body=message,
                         from_email=sender, to=recipient_list)
    email.content_subtype = 'html'
    if cc_list:
        email.cc = cc_list
    if bcc_list:
        email.bcc = bcc_list
    if reply_to:
        email.headers = {'Reply-To': reply_to}
    email.send()
