import os

from django.core.mail import EmailMessage
from django.template import Context, Template
from django.template.loader import get_template


def send_templated_email(subject, template, user=None, context=None, recipients=None, bcc=None,
                         attachment_filepath=None, attachments=None, headers=None, additional_args=None):
    """
    :param subject:         Subject of the email
    :param template:        Html Template used for sending email
    :param user:            User who requested to send the email
    :param context:         Context to send in HTML file
    :param recipients:      Whom to send email
    :param bcc:             Any BCC to send email
    :param attachment_filepath: Filepaths of attachements
    :param attachments:     Files to attach in emails
    :param headers:         Any specific headers
    :param additional_args: Any additional args
    :return:
    """
    content = get_template(template).render(context)
    # if not recipients are given then send the mail to the user
    if not recipients:
        recipients = [user.email]

    subject = Template(subject).render(Context(context))

    additional_args = additional_args or {}

    message = EmailMessage(subject,
                           content,
                           to=recipients,
                           bcc=bcc,
                           headers=headers, **additional_args)

    message.content_subtype = 'html'

    if attachment_filepath:
        file_object = open(attachment_filepath, 'r')
        file_name = os.path.basename(file_object.name)
        read_file_object = file_object.read()
        message.attach(file_name, read_file_object)

    if attachments:
        for filename, content, mime_type in attachments:
            message.attach(filename, content, mime_type)

    return message.send()
