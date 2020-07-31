from django.contrib import admin

from apps.core.models import User, OneTimePassCode


class OneTimePassCodeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'valid_until'
    )
    search_fields = (
        'user',
    )

    def get_queryset(self, request):
        """Get the team so we don't have hundreds of queries."""
        return super(
            OneTimePassCodeAdmin, self
        ).get_queryset(
            request
        ).select_related(
            'user'
        )


admin.site.register(OneTimePassCode, OneTimePassCodeAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'phone_number',
        'is_staff',
        'date_joined'
    )

    search_fields = (
        'first_name',
        'email',
        'phone_number'
    )


admin.site.register(User, UserAdmin)
