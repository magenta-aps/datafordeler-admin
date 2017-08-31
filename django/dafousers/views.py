# from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse
from django.http import HttpResponseRedirect
from dafousers.models import PasswordUser, UserIdentification
from dafousers.forms import PasswordUserForm


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


class PasswordUserCreate(CreateView):
    template_name = 'dafousers/passworduser-create.html'
    form_class = PasswordUserForm
    model = PasswordUser

    def form_valid(self, form):
        form.instance.changed_by = self.request.user.username

        userId = UserIdentification(user_id=form.instance.email)
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

        if request.POST.get("_addanother"):
            return HttpResponseRedirect(reverse('dafousers:passworduser-add'))
        elif request.POST.get("_save"):  # You can use else in here too if there is only 2 submit types.
            return HttpResponseRedirect(reverse('dafousers:passworduser-list'))


class PasswordUserList(ListView):
    template_name = 'dafousers/passworduser-list.html'
    model = PasswordUser

class PasswordUserDetails(DetailView):
    template_name = 'dafousers/passworduser-details.html'
    model = PasswordUser