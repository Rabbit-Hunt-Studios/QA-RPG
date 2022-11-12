from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse


class CancelAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(self,
                             request,
                             provider_id,
                             error=None,
                             exception=None,
                             extra_context=None):
        raise ImmediateHttpResponse(
            HttpResponseRedirect(reverse("account_login"))
        )