from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import Profile


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = Profile
    template_name = 'profiles/profile_form.html'
    success_url = reverse_lazy('profile')

    def dispatch(self, request, *args, **kwargs):
        self.fields = ('first_name', 'last_name', 'birthdate',)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form, **kwargs):
        form.instance.email = self.request.user.email
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs.get('pk')
        return reverse_lazy('profile', kwargs={'pk': pk})

    def get(self, request, *args, **kwargs):
        if request.user.id != self.kwargs.get('pk'):
            raise Http404
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.id == self.kwargs.get('pk'):
            raise Http404
        return super().post(request, *args, **kwargs)

    def test_func(self):
        return True


@login_required
def profile(request, pk):
    profile_data = Profile.objects.get(user=request.user)
    return render(request, 'profiles/profile.html', {'profile': profile_data,})
