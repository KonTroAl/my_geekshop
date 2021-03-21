from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.contrib import auth, messages
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.http import Http404

from authapp.forms import UserLoginForm, UserRegisterForm, UserProfileForm, ShopUserProfileEditForm
from basketapp.models import Basket
from authapp.models import User
from authapp.utils import send_verify_mail


# Create your views here.

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'authapp/login.html'

# def login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST['username']
#             password = request.POST['password']
#             user = auth.authenticate(username=username, password=password)
#             if user and user.is_active:
#                 auth.login(request, user)
#                 return HttpResponseRedirect(reverse('index'))
#     else:
#         form = UserLoginForm()
#
#     context = {'form': form}
#     return render(request, 'authapp/login.html', context)


class UserCreateView(CreateView):
    model = User
    template_name = 'authapp/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('auth:login')

    def form_valid(self, form):
        self.object = form.save()
        send_verify_mail(self.object)
        messages.success(self.request,
                         'Вы успешно зарегестрировались! Проверьте почту для активации аккаунта на нашем сайте!')
        return super().form_valid(form)


# def register(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(data=request.POST)
#         if form.is_valid():
#             user = form.save()
#             send_verify_mail(user)
#             messages.success(request,
#                              'Вы успешно зарегестрировались! Проверьте почту для активации аккаунта на нашем сайте!')
#             return HttpResponseRedirect(reverse('auth:login'))
#     else:
#         form = UserRegisterForm()
#     context = {'form': form}
#
#     return render(request, 'authapp/register.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


# class UserProfileView(UpdateView):
#     model = User
#     template_name = 'authapp/profile.html'
#     form_class = UserProfileForm
#
#     # def get_context_data(self, **kwargs):
#     #     context = super(UserProfileView, self).get_context_data(**kwargs)
#     #     context['profile_form'] = ShopUserProfileEditForm(instance=pk.shopuserprofile)
#     #     return context
#
#     def get_success_url(self):
#         return reverse_lazy('auth:profile', args=[self.kwargs['pk']])
#
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super(UserProfileView, self).dispatch(request, *args, **kwargs)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(data=request.POST, files=request.FILES, instance=request.user)
        profile_form = ShopUserProfileEditForm(data=request.POST, instance=request.user.shopuserprofile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse('auth:profile'))
    else:
        form = UserProfileForm(instance=request.user)
        profile_form = ShopUserProfileEditForm(instance=request.user.shopuserprofile)

    context = {
        'title': 'Profile',
        'form': form,
        'profile_form': profile_form,
        'baskets': Basket.objects.filter(user=request.user),
    }

    return render(request, 'authapp/profile.html', context)


def verify(request, user_id, hash):
    user = get_object_or_404(User, pk=user_id)
    if user.activation_key == hash and not user.is_activation_key_expired():
        user.is_active = True
        user.activation_key = None
        user.save()
        auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return render(request, 'authapp/verification.html')
