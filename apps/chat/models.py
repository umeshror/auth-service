from django.db import models
from django.db.models import Q

from apps.core.models import AuditMixin
from config.settings import AUTH_USER_MODEL


class ConversationManager(models.Manager):
    def get_user_conversations(self, user):
        """
        Returns all User Conversations.
        :param user: <USer Instance>: User object
        :return: <Queryset>: Unique Conversations
        """
        lookup_1 = Q(first=user) | Q(second=user)
        lookup_2 = Q(first=user) & Q(second=user)
        return self.get_queryset(). \
            filter(lookup_1). \
            exclude(lookup_2). \
            distinct(). \
            prefetch_related('first',
                             'second',
                             )

    def get_conversation(self, user1, user2):
        """
        Looks if Conversation exist for given users
        If found then returns
        :param user1: <User object>
        :param user2: <User object>
        :return: If found <Conversation Object>
        :return: If not found None
        """
        # If sender and receivers are same then no Conversation
        if user1 == user2:
            return

        # As Sender and Reciever can be assigned to any user object
        # create 2 different lookups
        lookup_1 = Q(first=user1) & Q(second=user2)

        lookup_2 = Q(first=user2) & Q(second=user1)

        try:
            return self.get_queryset().get(lookup_1 | lookup_2)
        except Conversation.DoesNotExist:
            return

    def get_or_new(self, sender, receiver):
        """
        Looks if Conversation exists for given Sender and Receivers
        If found return
        else create a new Conversation

        :param sender: <User object> : User who has sent the message
        :param receiver: <User object> : User whom the message is sent
        :return: <Conversation Object>
        """
        conversation = self.get_conversation(sender, receiver)
        if not conversation:
            conversation = self.create(first=sender,
                                       second=receiver,
                                       created_by=sender)
        return conversation


class Conversation(AuditMixin):
    """
    Chat window/Room
    Conversation is unique to sender and receiver
    """
    first = models.ForeignKey(AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              help_text="Speaker will get store here",
                              related_name='chat_conversation_first')

    second = models.ForeignKey(AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               help_text="Listener/Thrapist/Psychiatrist will get stored her",
                               related_name='chat_conversation_second')

    updated = models.DateTimeField(auto_now=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ConversationManager()

    class Meta:
        unique_together = ('first', 'second')

    def __unicode__(self):
        return self.id

    def get_speaker(self, user):
        """
        Gives speaker of the Conversation with respect to the user Sent
        :return:
        """
        if user not in [self.first, self.second]:
            return
        if user == self.first:
            return self.second
        return self.first

    def broadcast(self, msg=None):
        if msg is not None:
            # broadcast_msg_to_chat(msg, group_name=self.room_group_name, user='admin')
            return True
        return False

    def get_timestamp(self):
        """
        Gives readable datetime format
        :return: Aug 2, 1:30 PM
        """
        return self.timestamp.strftime('%b %-d, %-I:%M %p')


class ChatMessage(models.Model):
    """
    Chat messages
    """
    conversation = models.ForeignKey(Conversation,
                                     on_delete=models.CASCADE)

    author = models.ForeignKey(AUTH_USER_MODEL,
                               on_delete=models.CASCADE)

    message = models.TextField(editable=False)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __unicode__(self):
        return self.id

    def get_timestamp(self):
        """
        Gives readable datetime format
        :return: Aug 2, 1:30 PM
        """
        return self.timestamp.strftime('%b %-d, %-I:%M %p')

    def to_data(self):
        return {
            'id': self.id,
            'author': self.author.get_full_name(),
            'content': self.message,
            'timestamp': self.get_timestamp()
        }
