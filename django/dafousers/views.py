# from django.shortcuts import render

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


class PasswordUserCreate(CreateView):
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


class PasswordUserList(ListView):
    template_name = 'dafousers/passworduser-list.html'
    model = models.PasswordUser

    def get_context_data(self,**kwargs):
        context = super(PasswordUserList,self).get_context_data(**kwargs)
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