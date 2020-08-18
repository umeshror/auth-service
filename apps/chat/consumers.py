import json

from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from apps.chat.models import Conversation, ChatMessage
from apps.core.models import User


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        """
        When the Socket gets connected
        :param event:
        :return:
        """
        sender = self.scope['user']
        if sender.is_anonymous:
            return
        user_id = self.scope['url_route']['kwargs']['user_id']

        try:
            receiver = User.objects.get(id=int(user_id))
        except User.DoesNotExist:
            return
        self.conversation = await self.get_conversation(sender, receiver)

        self.conversation_name = str(self.conversation.id)

        await self.channel_layer.group_add(
            self.conversation_name,
            self.channel_name
        )

        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_disconnect(self, event):
        """
        When the Socket gets disconnected
        :param event:
        :return:
        """

        await self.channel_layer.group_discard(
            self.conversation_name,
            self.channel_name
        )

    async def websocket_receive(self, event):
        """
        When a message is received from WebSocket
        :param event: {'type': 'websocket.receive',
                        'text': 'Hello from web'}
        :return:
        """
        data_received = event.get('text')
        if not data_received:
            return

        data = json.loads(data_received)
        message = data['message']

        await self.new_message(message)

    async def new_message(self, message):
        """
        Send the newly send message to other Active Sockets
        who are chatting in the same group
        :param message: <Text>: Message written
        """
        user = self.scope['user']
        response_data = {
            'message': message,
            'username': user.get_full_name()
        }
        await self.create_chat_message(user, message)
        await self.channel_layer.group_send(
            self.conversation_name,
            {
                'type': 'chat_message',
                'response_data': json.dumps(response_data)
            }
        )

    async def chat_message(self, event):
        """
        custom event method
        Sends the actual message
        :param event:
        :return:
        """
        await self.send(
            {'type': "websocket.send",
             'text': event['response_data']}
        )

    @database_sync_to_async
    def get_conversation(self, sender, receiver):
        """
        Looks if Conversation exists for given Sender and Receivers
        If found return
        else create a new Conversation
        :param sender: <User object> : User who has sent the message
        :param receiver: <User object> : User whom the message is sent
        :return: <Conversation Object>
        """
        return Conversation.objects.get_or_new(sender, receiver)

    @database_sync_to_async
    def create_chat_message(self, author, message):
        """
        Save this Chat message to DB
        :param author: <User instance>: User who is sending the message
        :param message: <Text>: Message written
        :return: <ChatMessage instance>
        """

        return ChatMessage.objects.create(conversation=self.conversation,
                                          author=author,
                                          message=message)

