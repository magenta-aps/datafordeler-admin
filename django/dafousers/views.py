# from django.shortcuts import render

import urllib
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import _get_login_redirect_url
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from dafousers import models, model_constants, forms


# Create your views here.
class IndexView(TemplateView):
    template_name = 'start.html'


class FrontpageView(TemplateView):
    template_name = 'frontpage.html'


class LoginRequiredMixin(object):
    """Include to require login."""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Check for login and dispatch the view."""
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class LoginView(TemplateView):
    template_name = 'dafousers/login.html'
    redirect_field_name = 'next'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True
    process_django_login = False

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch_to_django_auth(self, request):
        # This code is copy/pasted from login in django.contrib.auth.views.
        # This is needed to avoid problems with csrf.
        redirect_to = request.POST.get(
            self.redirect_field_name,
            request.GET.get(self.redirect_field_name, '')
        )

        if self.redirect_authenticated_user and request.user.is_authenticated:
            redirect_to = _get_login_redirect_url(request, redirect_to)
            if redirect_to == request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. "
                    "Check that your LOGIN_REDIRECT_URL doesn't point to "
                    "a login page."
                )
            return HttpResponseRedirect(redirect_to)
        elif request.method == "POST" and self.process_django_login:
            form = self.authentication_form(request, data=request.POST)
            if form.is_valid():
                auth_login(request, form.get_user())
                return HttpResponseRedirect(_get_login_redirect_url(
                        request, redirect_to
                ))
        else:
            form = self.authentication_form(request)

        current_site = get_current_site(request)

        context = {
            'form': form,
            self.redirect_field_name: redirect_to,
            'site': current_site,
            'site_name': current_site.name,
        }

        return TemplateResponse(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        kwargs['idps'] = models.IdentityProviderAccount.objects.all()
        return kwargs

    def get(self, request, *args, **kwargs):
        # Dispatch to Django login to get redirect or context from there
        result = self.dispatch_to_django_auth(request)
        if isinstance(result, TemplateResponse):
            kwargs.update(result.context_data)
            return super(LoginView, self).get(request, *args, **kwargs)
        else:
            return result

    def post(self, request, *args, **kwargs):
        self.process_django_login = True
        # Check for a chosen idp and redirect to SSO proxy service if one is
        # present.
        idp_pk = request.POST.get('idp', None)
        if idp_pk is not None:
            self.process_django_login = False
            try:
                idp = models.IdentityProviderAccount.objects.get(pk=idp_pk)
                # Redirect to URL proxy service
                return HttpResponseRedirect(
                    settings.IDP_SSOPROXY_URL + '?' +
                    urllib.urlencode((
                        ('dafo_ssoproxy_url', request.build_absolute_uri()),
                        ('dafo_ssoproxy_idp', idp.name),
                        ('dafo_ssoproxy_returnparam', 'token')
                    ))
                )
            except models.IdentityProviderAccount.DoesNotExist:
                # continue to other login forms
                pass

        token = request.POST.get('token')
        if token is not None:
            self.process_django_login = False
            # Dispatch to authentification backend
            user = authenticate(token=token)
            if user is not None:
                auth_login(request, user)
                request.session['user_token'] = token

        # Dispatch to Django login to get redirect or context from there
        result = self.dispatch_to_django_auth(request)
        if isinstance(result, TemplateResponse):
            kwargs.update(result.context_data)
            return super(LoginView, self).get(request, *args, **kwargs)
        else:
            return result


class PasswordUserCreate(CreateView):
    template_name = 'dafousers/passworduser-create.html'
    form_class = forms.PasswordUserForm
    model = models.PasswordUser

    def form_valid(self, form):
        form.instance.changed_by = self.request.user.username

        userId = models.UserIdentification(user_id=form.instance.email)
        userId.save()
        form.instance.identified_user = userId
        salt, encrypted_password = \
            form.instance.generate_encrypted_password_and_salt(
                form.cleaned_data['password']
            )
        form.instance.password_salt = salt
        form.instance.encrypted_password = encrypted_password

        self.object = form.save(commit=False)
        self.object.save()
        form.instance.user_profiles = form.cleaned_data['user_profiles']

        return super(PasswordUserCreate, self).form_valid(form)

    def post(self, request, *args, **kwargs):

        super(CreateView, self).post(request, *args, **kwargs)

        for key, value in request.POST.items():
            print(key, value)

        action = request.POST.get('action')
        if action == '_addanother':
            return HttpResponseRedirect(reverse('dafousers:passworduser-add'))
        elif action == '_save':
            return HttpResponseRedirect(reverse('dafousers:passworduser-list'))


class PasswordUserList(ListView):
    template_name = 'dafousers/passworduser-list.html'
    model = models.PasswordUser

    def get_context_data(self, **kwargs):
        context = super(PasswordUserList, self).get_context_data(**kwargs)
        context['action'] = ""
        return context

    def post(self, request, *args, **kwargs):
        constants = model_constants.AccessAccount
        ids = request.POST.getlist('user_id')
        users = models.PasswordUser.objects.filter(id__in=ids)

        if request.POST.get("_status_active"):
            users.update(status=constants.STATUS_ACTIVE)
        elif request.POST.get("_status_blocked"):
            users.update(status=constants.STATUS_BLOCKED)
        elif request.POST.get("_status_deactive"):
            users.update(status=constants.STATUS_DEACTIVATED)

        return HttpResponseRedirect(reverse('dafousers:passworduser-list'))


class PasswordUserDetails(DetailView):
    template_name = 'dafousers/passworduser-details.html'
    model = models.PasswordUser
