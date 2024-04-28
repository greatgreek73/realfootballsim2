# clubs/views.py
from django.views.generic import CreateView, DetailView
from .models import Club
from .forms import ClubForm

class CreateClubView(CreateView):
    model = Club
    form_class = ClubForm
    template_name = 'clubs/create_club.html'
    success_url = '/clubs/detail/'  # предполагается, что пользователь перейдет на страницу деталей после создания

class ClubDetailView(DetailView):
    model = Club
    template_name = 'clubs/club_detail.html'
