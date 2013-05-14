"""OAuth backend for Facebook login."""
import cgi
import json
import urllib

import requests

from .base import OAuthBase, OAuthError


class FacebookOAuth(OAuthBase):
    authorize_url = 'https://graph.facebook.com/oauth/authorize'
    access_token_url = 'https://graph.facebook.com/oauth/access_token'
    profile_url = 'https://graph.facebook.com/me'
    profile_fields = [
        'username',
        'first_name',
        'middle_name',
        'last_name',
        'name',
        'locale',
        'gender',
        'timezone',
        'email',
        ]


    def __init__(self, redirect_uri, client_id, client_secret):
        self.redirect_uri = redirect_uri
        self.client_id = client_id
        self.client_secret = client_secret


    def get_authorize_url(self):
        """Return Facebook OAuth authorization URL."""
        return self.authorize_url + '?' + urllib.urlencode(
            {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'scope': 'email',
                }
            )


    def get_user_data(self, request_args):
        """
        Return dictionary of user data for given oauth request data.

        ``request_args`` is the querystring args in the redirected request from
        Facebook's auth URL.

        If no OAuth code is found, raise ``OAuthError``.

        """
        if 'code' not in request_args:
            raise OAuthError(
                "Sorry, we couldn't get your login info from Facebook!")

        access_token = self.get_access_token(request_args['code'])
        return self.get_profile(access_token)


    def get_access_token(self, code):
        """Get OAuth access token given code."""
        response = requests.get(
            self.access_token_url,
            params={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri,
                }
            )

        if response.status_code >= 400:
            raise OAuthError(json.loads(response.text)['error']['message'])

        data = cgi.parse_qs(response.text)

        return data['access_token'][-1]


    def get_profile(self, access_token):
        """Get user profile data given access token."""
        data = requests.get(
            self.profile_url + '?fields=' + ','.join(self.profile_fields),
            params={'access_token': access_token},
            ).json()

        return {k:v for k,v in data.items() if k in self.profile_fields}
