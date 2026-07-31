from oauth2_provider.oauth2_validators import OAuth2Validator


class MindCareOAuth2Validator(OAuth2Validator):
    """
    Adds the standard OIDC claims LibreChat's OpenID strategy maps onto its
    own user record (email, name) to the ID token, on top of the default
    `sub` claim django-oauth-toolkit already includes.
    """

    def get_additional_claims(self, request):
        user = request.user
        return {
            "sub": str(user.id),
            "email": user.email,
            "email_verified": user.is_email_verified,
            "name": user.full_name,
            "given_name": user.first_name,
            "family_name": user.last_name,
        }
