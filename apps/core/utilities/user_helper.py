from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import User


def get_user_by_email(email):
    """

    :param email: user@example.com
    :return: if found : User instance
    :return: if not found : Raise
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise Exception("We couldn't find an account with this email,"
                        " please verify the email you entered.")
    return user


def get_jwt_token(user):
    """
    Create JWT token for given user
    :param user: User instance
    :return: {
        'access': str : access_token,
        'refresh': str : refresh_token
    }
    """
    # Give access token for further API interactions
    token = RefreshToken.for_user(user)
    return {
        'access': str(token.access_token),
        'refresh': str(token)
    }
