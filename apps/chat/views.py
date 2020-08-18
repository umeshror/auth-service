from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from apps.chat.models import Conversation, ChatMessage
from apps.core.models import User


class MessageSerializer(serializers.ModelSerializer):
    timestamp = serializers.CharField(source='get_timestamp')

    class Meta:
        model = ChatMessage
        fields = ('author_id',
                  'message',
                  'timestamp')


class MessageAPIPagination(PageNumberPagination):
    page_size = 50


class MessagesAPIView(ListAPIView):
    pagination_class = MessageAPIPagination
    serializer_class = MessageSerializer

    def get_queryset(self):
        receiver_id = self.kwargs['receiver_id']
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            raise NotFound("We couldn't find an Receiver with given id")

        # logged in User is the sender
        sender = self.request.user

        conversation = Conversation.objects.get_conversation(user1=sender,
                                                 user2=receiver)

        if not conversation:
            return []
        return conversation.chatmessage_set.all()
