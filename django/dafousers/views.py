# -*- coding: utf-8 -*-
# from django.shortcuts import render

from dafousers.auth import update_user_auth_info
from dafousers import models, model_constants, forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import _get_login_redirect_url
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.db.models import Min
from django.http import HttpResponseRedirect
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.edit import CreateView
from django.views.generic import View, TemplateView, UpdateView
from django.views.generic.list import ListView

import json
import tempfile
import urllib


# Create your views here.
class IndexView(TemplateView):
    template_name = 'start.html'


class FrontpageView(TemplateView):
    template_name = 'frontpage.html'


class LoginRequiredMixin(object):
    """Include to require login."""

    needs_userprofiles = None
    needs_userprofiles_any = None
    needs_system_roles = None
    needs_system_roles_any = None

    def check_userprofiles(self):
        # If needs_userprofiles is defined check that the user has all
        # the needed permissions
        if self.needs_userprofiles is not None:
            match_nr = self.authinfo.user_profiles.filter(
                name__in=self.needs_userprofiles
            ).count()
            if match_nr < len(self.needs_userprofiles):
                raise PermissionDenied(
                    "User does not have all neccessary userprofiles: %s" % (
                        self.needs_userprofiles
                    )
                )
        # If needs_userprofiles_any is defined check that the user has any
        # of the specified_permissions
        if self.needs_userprofiles_any is not None:
            if not self.authinfo.user_profiles.filter(
                name__in=self.needs_userprofiles_any
            ).exists():
                raise PermissionDenied(
                    "User does not have any of the needed userprofiles: %s" % (
                        self.needs_userprofiles_any
                    )
                )

    def check_system_roles(self):
        if self.needs_system_roles is not None:
            match_nr = self.authinfo.system_roles.filter(
                role_name__in=self.needs_system_roles
            ).count()
            if match_nr < len(self.needs_system_roles):
                raise PermissionDenied(
                    "User does not have all neccessary system roles: %s" % (
                        self.needs_system_roles
                    )
                )
        if self.needs_system_roles_any is not None:
            if not self.authinfo.system_roles.filter(
                role_name__in=self.needs_system_roles_any
            ).exists():
                raise PermissionDenied(
                    "User does not have any of the needed system roles: %s" % (
                        self.needs_system_roles_any
                    )
                )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Check for login and dispatch the view."""

        self.authinfo = update_user_auth_info(self.request)
        self.check_userprofiles()
        self.check_system_roles()

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
                # Delete any lingering token from a previous login
                if "token" in request.session:
                    del request.session["token"]
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
                        ('dafo_ssoproxy_idp', idp.idp_entity_id),
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
                request.session['token'] = token
                redirect_to = request.POST.get(
                    self.redirect_field_name,
                    request.GET.get(self.redirect_field_name, '')
                )
                return HttpResponseRedirect(_get_login_redirect_url(
                        request, redirect_to
                ))

        # Dispatch to Django login to get redirect or context from there
        result = self.dispatch_to_django_auth(request)
        if isinstance(result, TemplateResponse):
            kwargs.update(result.context_data)
            return super(LoginView, self).get(request, *args, **kwargs)
        else:
            return result


class PasswordUserCreate(LoginRequiredMixin, CreateView):
    template_name = 'dafousers/passworduser/add.html'
    form_class = forms.PasswordUserForm
    model = models.PasswordUser
    needs_system_roles_any = ["DAFO Serviceudbyder", "DAFO Administrator"]

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

        result = super(PasswordUserCreate, self).form_valid(form)
        form.instance.user_profiles = form.cleaned_data['user_profiles']
        return result

    def post(self, request, *args, **kwargs):

        super(CreateView, self).post(request, *args, **kwargs)

        action = request.POST.get('action')
        if action == '_addanother':
            return HttpResponseRedirect(reverse('dafousers:passworduser-add'))
        elif action == '_save':
            return HttpResponseRedirect(reverse('dafousers:passworduser-list'))


class PasswordUserList(LoginRequiredMixin, ListView):
    template_name = 'dafousers/passworduser/list.html'
    model = models.PasswordUser

    def get_context_data(self, **kwargs):
        context = super(PasswordUserList, self).get_context_data(**kwargs)
        context['action'] = ""
        context['user_profiles'] = models.UserProfile.objects.all()
        context['filter'] = ''
        context['order'] = 'name'
        context['object_list'] = get_passworduser_queryset(context['filter'], context['order'])
        return context


class PasswordUserHistory(LoginRequiredMixin, ListView):
    template_name = 'dafousers/passworduser/history.html'
    model = models.PasswordUserHistory

    def get_context_data(self, **kwargs):
        context = super(PasswordUserHistory, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context['password_user_id'] = pk
        context['history'] = models.PasswordUserHistory.objects.filter(
            entity=models.PasswordUser.objects.get(pk=pk)
        ).order_by("-updated")
        return context


class PasswordUserEdit(LoginRequiredMixin, UpdateView):
    template_name = 'dafousers/passworduser/edit.html'
    model = models.PasswordUser
    form_class = forms.PasswordUserForm
    success_url = 'user/list/'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(PasswordUserEdit, self).get_form_kwargs(**kwargs)
        kwargs['pk'] = self.kwargs.get('pk')
        return kwargs

    def form_valid(self, form):
        form.instance.changed_by = self.request.user.username
        if form.cleaned_data['password'] != "*":
            salt, encrypted_password = form.instance.generate_encrypted_password_and_salt(form.cleaned_data['password'])
            form.instance.password_salt = salt
            form.instance.encrypted_password = encrypted_password

        self.object = form.save(commit=False)
        form.instance.user_profiles = form.cleaned_data['user_profiles']

        return super(PasswordUserEdit, self).form_valid(form)

    def post(self, request, *args, **kwargs):

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        action = request.POST.get('action')
        if action == '_save':
            result = super(PasswordUserEdit, self).post(request, *args, **kwargs)
            if form.is_valid():
                return HttpResponseRedirect(reverse('dafousers:passworduser-list'))
            else:
                return result


def update_passworduser(request):

    ids = request.POST.getlist('user_id')
    users = models.PasswordUser.objects.filter(id__in=ids)
    action = request.POST.get('action')
    if '_status' in action:
        parts = action.split("_")
        status = parts[2]
        users.update(status=status)
    elif action == '_add_user_profiles':
        user_profiles_ids = request.POST.getlist('user_profiles')
        user_profiles = models.UserProfile.objects.filter(id__in=user_profiles_ids)
        for user_profile in user_profiles:
            for user in users:
                user.user_profiles.add(user_profile)
    return HttpResponse("Success")


def update_passworduser_queryset(request):
    filter = request.GET.get('filter', None)
    order = request.GET.get('order', None)
    password_users = get_passworduser_queryset(filter, order)
    return render(request, 'dafousers/passworduser/table.html', {'object_list': password_users})


def get_passworduser_queryset(filter, order):
    # If a filter param is passed, we use it to filter
    if filter:
        password_users = models.PasswordUser.objects.filter(status=filter)
    else:
        password_users = models.PasswordUser.objects.all()

    # If a order param is passed, we use it to order
    if order:
        if order == "name":
            password_users = password_users.order_by("givenname", "lastname")
        elif order == "-name":
            password_users = password_users.order_by("-givenname", "-lastname")
        else:
            password_users = password_users.order_by(order)

    return password_users


class CertificateUserCreate(LoginRequiredMixin, CreateView):
    template_name = 'dafousers/certificateuser/add.html'
    form_class = forms.CertificateUserForm
    model = models.CertificateUser

    def form_valid(self, form):
        form.instance.changed_by = self.request.user.username

        user_id = models.UserIdentification(user_id=form.instance.contact_email)
        user_id.save()
        form.instance.identified_user = user_id

        result = super(CertificateUserCreate, self).form_valid(form)
        form.instance.user_profiles = form.cleaned_data['user_profiles']
        certificate_years_valid = form.cleaned_data['certificate_years_valid']
        form.instance.create_certificate(int(certificate_years_valid))
        return result

    def post(self, request, *args, **kwargs):

        result = super(CreateView, self).post(request, *args, **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            action = request.POST.get('action')
            if action == '_addanother':
                return HttpResponseRedirect(reverse('dafousers:certificateuser-add'))
            elif action == '_save':
                return HttpResponseRedirect(reverse('dafousers:certificateuser-list'))
        else:
            print "Error saving CertificateUser."
            print form.errors
            return result


class CertificateUserList(LoginRequiredMixin, ListView):
    template_name = 'dafousers/certificateuser/list.html'
    model = models.CertificateUser

    def get_context_data(self, **kwargs):
        context = super(CertificateUserList, self).get_context_data(**kwargs)
        context['action'] = ""
        context['user_profiles'] = models.UserProfile.objects.all()
        context['filter'] = ''
        context['order'] = 'name'
        context['object_list'] = get_certificateuser_queryset(context['filter'], context['order'])
        return context


class CertificateUserHistory(LoginRequiredMixin, ListView):
    template_name = 'dafousers/certificateuser/history.html'
    model = models.CertificateUserHistory

    def get_context_data(self, **kwargs):
        context = super(CertificateUserHistory, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context['certificate_user_id'] = pk
        context['history'] = models.CertificateUserHistory.objects.filter(
            entity=models.CertificateUser.objects.get(pk=pk)
        ).order_by("-updated")
        return context


class CertificateUserEdit(LoginRequiredMixin, UpdateView):
    template_name = 'dafousers/certificateuser/edit.html'
    model = models.CertificateUser
    form_class = forms.CertificateUserForm
    success_url = 'certificateuser/list/'
    create_new_certificate = False

    def get_form_kwargs(self, **kwargs):
        kwargs = super(CertificateUserEdit, self).get_form_kwargs(**kwargs)
        kwargs['pk'] = self.kwargs.get('pk')
        return kwargs

    def form_valid(self, form):
        form.instance.changed_by = self.request.user.username
        form.instance.user_profiles = form.cleaned_data['user_profiles']
        form.instance.certificates = form.cleaned_data['certificates']

        # Do we want to remove certs from the database?
        for cert in form.instance.certificates.all():
            removed_cert = form.cleaned_data['certificates'].filter(pk=cert.pk)
            if not removed_cert:
                form.instance.certificates.remove(cert.pk)

        if self.create_new_certificate:
            certificate_years_valid = form.cleaned_data['certificate_years_valid']
            print certificate_years_valid
            form.instance.create_certificate(int(certificate_years_valid))
        return super(CertificateUserEdit, self).form_valid(form)

    def post(self, request, *args, **kwargs):

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        self.create_new_certificate = request.POST.get('create_new_certificate')
        action = request.POST.get('action')
        if action == '_save':
            result = super(CertificateUserEdit, self).post(request, *args, **kwargs)
            if form.is_valid():
                return HttpResponseRedirect(reverse('dafousers:certificateuser-list'))
            else:
                print "Error saving CertificateUser."
                print form.errors
                return result


def update_certificateuser(request):

    ids = request.POST.getlist('user_id')
    systems = models.CertificateUser.objects.filter(id__in=ids)
    action = request.POST.get('action')
    if '_status' in action:
        parts = action.split("_")
        status = parts[2]
        systems.update(status=status)
    elif action == '_add_user_profiles':
        user_profiles_ids = request.POST.getlist('user_profiles')
        user_profiles = models.UserProfile.objects.filter(id__in=user_profiles_ids)
        for user_profile in user_profiles:
            for system in systems:
                system.user_profiles.add(user_profile)
    return HttpResponse("Success")


def update_certificateuser_queryset(request):
    filter = request.GET.get('filter', None)
    order = request.GET.get('order', None)
    password_users = get_certificateuser_queryset(filter, order)
    return render(request, 'dafousers/certificateuser/table.html', {'object_list': password_users})


def get_certificateuser_queryset(filter, order):
    # If a filter param is passed, we use it to filter
    if filter:
        certificate_users = models.CertificateUser.objects.filter(status=filter)
    else:
        certificate_users = models.CertificateUser.objects.all()

    # If a order param is passed, we use it to order
    if order:
        if "next_expiration_subject" in order:
            certificate_users = certificate_users.annotate(
                next_expiration_subject=Min('certificates__subject')
            )
        elif "next_expiration" in order:
            certificate_users = certificate_users.annotate(
                next_expiration=Min('certificates__valid_to')
            )
        certificate_users = certificate_users.order_by(order)
    return certificate_users


class IdentityProviderAccountCreate(LoginRequiredMixin, CreateView):
    template_name = 'dafousers/identityprovideraccount/add.html'
    form_class = forms.IdentityProviderAccountForm
    model = models.IdentityProviderAccount

    def form_valid(self, form):
        form.instance.changed_by = self.request.user.username

        user_id = models.UserIdentification(user_id=form.instance.contact_email)
        user_id.save()
        form.instance.identified_user = user_id

        result = super(IdentityProviderAccountCreate, self).form_valid(form)
        form.instance.user_profiles = form.cleaned_data['user_profiles']
        return result

    def post(self, request, *args, **kwargs):

        result = super(CreateView, self).post(request, *args, **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            action = request.POST.get('action')
            if action == '_addanother':
                return HttpResponseRedirect(reverse('dafousers:identityprovideraccount-add'))
            elif action == '_save':
                return HttpResponseRedirect(reverse('dafousers:identityprovideraccount-list'))
        else:
            return result


class IdentityProviderAccountList(LoginRequiredMixin, ListView):
    template_name = 'dafousers/identityprovideraccount/list.html'
    model = models.IdentityProviderAccount

    def get_context_data(self, **kwargs):
        context = super(IdentityProviderAccountList, self).get_context_data(**kwargs)
        context['action'] = ""
        context['user_profiles'] = models.UserProfile.objects.all()
        context['filter'] = ''
        context['order'] = 'name'
        context['object_list'] = get_identityprovideraccount_queryset(context['filter'], context['order'])
        return context


class IdentityProviderAccountHistory(LoginRequiredMixin, ListView):
    template_name = 'dafousers/identityprovideraccount/history.html'
    model = models.IdentityProviderAccountHistory

    def get_context_data(self, **kwargs):
        context = super(IdentityProviderAccountHistory, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context['identityprovider_account_id'] = pk
        context['history'] = models.IdentityProviderAccountHistory.objects.filter(
            entity=models.IdentityProviderAccount.objects.get(pk=pk)
        ).order_by("-updated")
        return context


class IdentityProviderAccountEdit(LoginRequiredMixin, UpdateView):
    template_name = 'dafousers/identityprovideraccount/edit.html'
    model = models.IdentityProviderAccount
    form_class = forms.IdentityProviderAccountForm
    success_url = 'identityprovideraccount/list/'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(IdentityProviderAccountEdit, self).get_form_kwargs(**kwargs)
        kwargs['pk'] = self.kwargs.get('pk')
        return kwargs

    def form_valid(self, form):
        form.instance.changed_by = self.request.user.username
        self.object = form.save(commit=False)
        form.instance.user_profiles = form.cleaned_data['user_profiles']

        return super(IdentityProviderAccountEdit, self).form_valid(form)

    def post(self, request, *args, **kwargs):

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        action = request.POST.get('action')
        if action == '_save':
            result = super(IdentityProviderAccountEdit, self).post(request, *args, **kwargs)
            if form.is_valid():
                return HttpResponseRedirect(reverse('dafousers:identityprovideraccount-list'))
            else:
                print "Error saving IdentityProviderAccount."
                print form.errors
                return result


def update_identityprovideraccount(request):

    ids = request.POST.getlist('user_id')
    organisations = models.IdentityProviderAccount.objects.filter(id__in=ids)
    action = request.POST.get('action')
    if '_status' in action:
        parts = action.split("_")
        status = parts[2]
        organisations.update(status=status)
    elif action == '_add_user_profiles':
        user_profiles_ids = request.POST.getlist('user_profiles')
        user_profiles = models.UserProfile.objects.filter(id__in=user_profiles_ids)
        for user_profile in user_profiles:
            for organisation in organisations:
                organisation.user_profiles.add(user_profile)
    return HttpResponse("Success")


def update_identityprovideraccount_queryset(request):
    filter = request.GET.get('filter', None)
    order = request.GET.get('order', None)
    identityprovider_accounts = get_identityprovideraccount_queryset(filter, order)
    return render(request, 'dafousers/identityprovideraccount/table.html', {'object_list': identityprovider_accounts})


def get_identityprovideraccount_queryset(filter, order):
    # If a filter param is passed, we use it to filter
    if filter:
        identityprovider_accounts = models.IdentityProviderAccount.objects.filter(status=filter)
    else:
        identityprovider_accounts = models.IdentityProviderAccount.objects.all()

    # If a order param is passed, we use it to order
    if order:
        identityprovider_accounts = identityprovider_accounts.order_by(order)
    return identityprovider_accounts


class UserProfileCreate(LoginRequiredMixin, CreateView):
    template_name = 'dafousers/userprofile/add.html'
    form_class = forms.UserProfileForm
    model = models.UserProfile

    def form_valid(self, form):
        form.instance.changed_by = self.request.user.username

        result = super(UserProfileCreate, self).form_valid(form)
        form.instance.system_roles = form.cleaned_data['system_roles']
        form.instance.area_restrictions = form.cleaned_data['area_restrictions']
        return result

    def post(self, request, *args, **kwargs):

        result = super(CreateView, self).post(request, *args, **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            action = request.POST.get('action')
            if action == '_addanother':
                return HttpResponseRedirect(reverse('dafousers:userprofile-add'))
            elif action == '_save':
                return HttpResponseRedirect(reverse('dafousers:userprofile-list'))
        else:
            return result


class UserProfileList(LoginRequiredMixin, ListView):
    template_name = 'dafousers/userprofile/list.html'
    model = models.UserProfile

    def get_context_data(self, **kwargs):
        context = super(UserProfileList, self).get_context_data(**kwargs)
        context['action'] = ""
        context['system_roles'] = models.SystemRole.objects.all()
        context['area_restrictions'] = models.AreaRestriction.objects.all()
        context['filter'] = ''
        context['order'] = 'name'
        context['object_list'] = get_userprofile_queryset(context['filter'], context['order'])
        return context


class UserProfileHistory(LoginRequiredMixin, ListView):
    template_name = 'dafousers/userprofile/history.html'
    model = models.UserProfileHistory

    def get_context_data(self, **kwargs):
        context = super(UserProfileHistory, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context['user_profile_id'] = pk
        context['history'] = models.UserProfileHistory.objects.filter(
            entity=models.UserProfile.objects.get(pk=pk)
        ).order_by("-updated")
        return context


class UserProfileEdit(LoginRequiredMixin, UpdateView):
    template_name = 'dafousers/userprofile/edit.html'
    model = models.UserProfile
    form_class = forms.UserProfileForm
    success_url = 'userprofile/list/'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(UserProfileEdit, self).get_form_kwargs(**kwargs)
        kwargs['pk'] = self.kwargs.get('pk')
        return kwargs

    def form_valid(self, form):
        form.instance.changed_by = self.request.user.username
        self.object = form.save(commit=False)
        form.instance.system_roles = form.cleaned_data['system_roles']
        form.instance.area_restrictions = form.cleaned_data['area_restrictions']

        return super(UserProfileEdit, self).form_valid(form)

    def post(self, request, *args, **kwargs):

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        action = request.POST.get('action')
        if action == '_save':
            result = super(UserProfileEdit, self).post(request, *args, **kwargs)
            if form.is_valid():
                return HttpResponseRedirect(reverse('dafousers:userprofile-list'))
            else:
                print "Error saving UserProfile."
                print form.errors
                return result


def update_userprofile(request):

    ids = request.POST.getlist('user_id')
    user_profiles = models.UserProfile.objects.filter(id__in=ids)
    action = request.POST.get('action')
    if '_status' in action:
        parts = action.split("_")
        status = parts[2]
        user_profiles.update(status=status)
    elif action == '_add_system_roles':
        system_roles_ids = request.POST.getlist('system_roles')
        system_roles = models.SystemRole.objects.filter(id__in=system_roles_ids)
        for system_role in system_roles:
            for user_profile in user_profiles:
                user_profile.system_roles.add(system_role)
    elif action == '_add_area_restrictions':
        area_restrictions_ids = request.POST.getlist('area_restrictions')
        area_restrictions = models.AreaRestriction.objects.filter(id__in=area_restrictions_ids)
        for area_restriction in area_restrictions:
            for user_profile in user_profiles:
                user_profile.area_restrictions.add(area_restriction)
    return HttpResponse("Success")


def update_userprofile_queryset(request):
    filter = request.GET.get('filter', None)
    order = request.GET.get('order', None)
    user_profiles = get_userprofile_queryset(filter, order)
    return render(request, 'dafousers/userprofile/table.html', {'object_list': user_profiles})


def get_userprofile_queryset(filter, order):
    # If a filter param is passed, we use it to filter
    if filter:
        user_profiles = models.UserProfile.objects.filter(status=filter)
    else:
        user_profiles = models.UserProfile.objects.all()

    # If a order param is passed, we use it to order
    if order:
        user_profiles = user_profiles.order_by(order)
    return user_profiles


def search_org_user_system(request):
    search_term = request.GET.get('search_term', None)
    result = []
    if search_term == "":
        return render(request, 'search-autocomplete.html', {'object_list': result})

    users = models.PasswordUser.objects.search(search_term)
    organisations = models.IdentityProviderAccount.objects.search(search_term)
    systems = models.CertificateUser.objects.search(search_term)

    for user in users:
        result.append({
            "text": "Bruger: " + user.givenname + " " + user.lastname,
            "url": reverse('dafousers:passworduser-edit', kwargs={"pk": user.id})
        })

    for organisation in organisations:
        result.append({
            "text": "Organisation: " + organisation.name,
            "url": reverse('dafousers:identityprovideraccount-edit', kwargs={"pk": organisation.id})
        })

    for system in systems:
        result.append({
            "text": "System: " + system.name,
            "url": reverse('dafousers:certificateuser-edit', kwargs={"pk": system.id})
        })

    return render(request, 'search-autocomplete.html', {'object_list': result})


def search_user_profile(request):
    search_term = request.GET.get('search_term', None)
    result = []
    if search_term == "":
        return render(request, 'org_user_system_auto.html', {'object_list': result})

    user_profiles = models.UserProfile.objects.search(search_term)

    for user_profile in user_profiles:
        result.append({
            "text": user_profile.name,
            "url": reverse('dafousers:userprofile-edit', kwargs={"pk": user_profile.id})
        })

    return render(request, 'search-autocomplete.html', {'object_list': result})


class CertificateDownload(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        cert = models.Certificate.objects.get(pk=kwargs.get('pk'))
        filename = cert.valid_to
        tmp_file = tempfile.TemporaryFile()
        tmp_file.write(cert.certificate_blob)
        tmp_file.seek(0)
        resp = HttpResponse(tmp_file, content_type='text/html')
        resp['Content-Disposition'] = "attachment; filename=cert_%s.crt" % filename
        return resp
