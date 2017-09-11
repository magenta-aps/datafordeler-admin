# from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, UpdateView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from dafousers import models, model_constants, forms
from model_constants import AccessAccount as constants
import urllib, json


# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'


class FrontpageView(TemplateView):
    template_name = 'frontpage.html'


class LoginRequiredMixin(object):
    """Include to require login."""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Check for login and dispatch the view."""
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class PasswordUserCreate(LoginRequiredMixin, CreateView):
    template_name = 'dafousers/passworduser/add.html'
    form_class = forms.PasswordUserForm
    model = models.PasswordUser

    def form_valid(self, form):
        form.instance.changed_by = self.request.user.username

        userId = models.UserIdentification(user_id=form.instance.email)
        userId.save()
        form.instance.identified_user = userId
        salt, encrypted_password = form.instance.generate_encrypted_password_and_salt(form.cleaned_data['password'])
        form.instance.password_salt = salt
        form.instance.encrypted_password = encrypted_password

        self.object = form.save(commit=False)
        self.object.save()
        form.instance.user_profiles = form.cleaned_data['user_profiles']

        return super(PasswordUserCreate, self).form_valid(form)

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

    def get_context_data(self,**kwargs):
        context = super(PasswordUserList,self).get_context_data(**kwargs)
        context['action'] = ""
        context['user_profiles'] = models.UserProfile.objects.all()

        context['order'] = self.get_order()
        context['filter'] = self.get_filter()

        if context['filter'] == 'active':
            context['object_list'] = models.PasswordUser.objects.filter(status=constants.STATUS_ACTIVE)
        elif context['filter'] == 'blocked':
            context['object_list'] = models.PasswordUser.objects.filter(status=constants.STATUS_BLOCKED)
        elif context['filter'] == 'deactivated':
            context['object_list'] = models.PasswordUser.objects.filter(status=constants.STATUS_DEACTIVATED)
        else:
            context['object_list'] = models.PasswordUser.objects.all()

        if context['order'] == "name":
            context['object_list'] = context['object_list'].order_by("givenname", "lastname")
        elif context['order'] == "-name":
            context['object_list'] = context['object_list'].order_by("-givenname", "-lastname")

        return context

    def get_order(self):
        return self.request.GET.get('order', 'name')

    def get_filter(self):
        return self.request.GET.get('filter', '')

    def get_redirect(self, url, params):
        url += "?" + urllib.urlencode(params)
        return HttpResponseRedirect(url)

    def post(self, request, *args, **kwargs):

        ids = request.POST.getlist('user_id')
        users = models.PasswordUser.objects.filter(id__in=ids)

        action = request.POST.get('action')
        print action
        if action == '_status_active':
            users.update(status=constants.STATUS_ACTIVE)
        elif action == '_status_blocked':
            users.update(status=constants.STATUS_BLOCKED)
        elif action == '_status_deactive':
            users.update(status=constants.STATUS_DEACTIVATED)
        elif action == '_add_user_profiles':
            user_profiles_ids = request.POST.getlist('user_profiles')
            user_profiles = models.UserProfile.objects.filter(id__in=user_profiles_ids)
            print user_profiles
            for user_profile in user_profiles:
                for user in users:
                    user.user_profiles.add(user_profile)

        params = {}
        filter = self.get_filter()
        post_filter = request.POST.get('filter')
        if post_filter != filter:
            filter = post_filter
        if filter is not None:
            params["filter"] = filter

        order = self.get_order()
        post_order = request.POST.get('order')
        if post_order != order:
            order = post_order
        if order is not None:
            params["order"] = order

        return self.get_redirect(reverse('dafousers:passworduser-list'), params)


class PasswordUserHistory(LoginRequiredMixin, ListView):
    template_name = 'dafousers/passworduser/history.html'
    model = models.PasswordUserHistory

    def get_context_data(self, **kwargs):
        context = super(PasswordUserHistory, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context['password_user_id'] = pk
        context['history'] = models.PasswordUserHistory.objects.filter(entity=models.PasswordUser.objects.get(pk=pk))
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
        self.object.save()
        form.instance.user_profiles = form.cleaned_data['user_profiles']

        return super(PasswordUserEdit, self).form_valid(form)

    def post(self, request, *args, **kwargs):

        result = super(PasswordUserEdit, self).post(request, *args, **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            action = request.POST.get('action')
            if action == '_goto_history':
                return HttpResponseRedirect(reverse('dafousers:passworduser-history', kwargs={"pk": self.object.id}))
            elif action == '_save':
                return HttpResponseRedirect(reverse('dafousers:passworduser-list'))
        else:
            return result


class CertificateUserCreate(LoginRequiredMixin, CreateView):
    template_name = 'dafousers/certificateuser/add.html'
    form_class = forms.CertificateUserForm
    model = models.CertificateUser

    def form_valid(self, form):
        form.instance.changed_by = self.request.user.username

        user_id = models.UserIdentification(user_id=form.instance.contact_email)
        user_id.save()
        form.instance.identified_user = user_id

        self.object = form.save(commit=False)
        self.object.save()
        form.instance.user_profiles = form.cleaned_data['user_profiles']
        form.instance.certificates = form.cleaned_data['certificates']

        return super(CertificateUserCreate, self).form_valid(form)

    def post(self, request, *args, **kwargs):

        result = super(CreateView, self).post(request, *args, **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            action = request.POST.get('action')
            if action == '_addanother':
                return HttpResponseRedirect(reverse('dafousers:certificateuser-add'))
            elif action == '_save':
                return HttpResponseRedirect(reverse('dafousers:passworduser-list'))
        else:
            return result


def search_org_user_system(request):
    search_term = request.GET.get('search_term', None)
    result = []
    if search_term == "":
        return render(request, 'org_user_system_auto.html', {'object_list': result})

    users = models.PasswordUser.objects.search(search_term)
    organisations = models.IdentityProviderAccount.objects.search(search_term)
    systems = models.CertificateUser.objects.search(search_term)

    for user in users:
        result.append({
            "text": "Bruger: " + user.givenname + " " + user.lastname,
            "url": reverse('dafousers:passworduser-details', kwargs={"pk": user.id})
        })

    for organisation in organisations:
        result.append({
            "text": "Organisation: " + organisation.name,
            "url": reverse('dafousers:passworduser-details', kwargs={"pk": organisation.id})
        })

    for system in systems:
        result.append({
            "text": "System: " + system.name,
            "url": reverse('dafousers:passworduser-details', kwargs={"pk": system.id})
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
            "url": reverse('dafousers:passworduser-details', kwargs={"pk": user_profile.id})
        })

    return render(request, 'search-autocomplete.html', {'object_list': result})


def update_passworduser_queryset(request):
    filter = request.GET.get('filter', None)
    order = request.GET.get('order', None)

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

    return render(request, 'dafousers/passworduser/table.html', {'object_list': password_users})
