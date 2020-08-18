from django.contrib import admin

from .models import Conversation, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage

    fields = ('sender', 'message')
    readonly_fields = ('message',)


class ConversationAdmin(admin.ModelAdmin):
    inlines = [ChatMessageInline]

    list_display = (
        'get_sender_name',
        'get_receiver_name',
        'timestamp'
    )

    search_fields = ('first__email',
                     'first__first_name',
                     'first__last_name',
                     'second__email',
                     'second__first_name',
                     'second__last_name')
    class Meta:
        model = Conversation

    def get_sender_name(self, obj):
        return obj.first.get_full_name()

    def get_receiver_name(self, obj):
        return obj.second.get_full_name()

    def get_queryset(self, request):
        """
        Fetches related crop, team and category information
        :param request:
        :return: Queryset
        """
        return super(
            ConversationAdmin,
            self
        ).get_queryset(
            request
        ).select_related(
            'first',
            'second'
        ).prefetch_related(
            'chatmessage_set',
        )

    get_sender_name.short_description = 'Sender'
    get_receiver_name.short_description = 'Receiver'

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        'get_sender_name',
        'conversation',
        'message',
        'timestamp'
    )

    search_fields = ('author__email',
                     'author__first_name',
                     'author__last_name'
                     )
    class Meta:
        model = ChatMessage

    def get_sender_name(self, obj):
        return obj.sender.get_full_name()

    def get_queryset(self, request):
        """
        Fetches related crop, team and category information
        :param request:
        :return: Queryset
        """
        return super(
            ChatMessageAdmin,
            self
        ).get_queryset(
            request
        ).select_related(
            'sender'
        )

admin.site.register(Conversation, ConversationAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
