# from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse
from django.http import HttpResponseRedirect
from dafousers import models, model_constants, forms


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
    template_name = 'dafousers/passworduser-create.html'
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
    template_name = 'dafousers/passworduser-list.html'
    model = models.PasswordUser

    def get_context_data(self,**kwargs):
        context = super(PasswordUserList,self).get_context_data(**kwargs)
        context['action'] = ""
        context['ordering'] = self.get_ordering()
        return context

    def get_ordering(self):
        return self.request.GET.get('ordering', 'organisation')

    def post(self, request, *args, **kwargs):
        for key, value in request.POST.items():
            print(key, value)
        constants = model_constants.AccessAccount
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

        ordering = self.get_ordering()
        return HttpResponseRedirect(reverse('dafousers:passworduser-list') + "?ordering=" + ordering)

class PasswordUserDetails(LoginRequiredMixin, DetailView):
    template_name = 'dafousers/passworduser-details.html'
    model = models.PasswordUser