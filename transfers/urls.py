from django.urls import path
from . import views

app_name = 'transfers'  # Это важно для пространства имен URL

urlpatterns = [
    path('market/', views.transfer_market, name='transfer_market'),
    path('listing/<int:listing_id>/', views.transfer_listing_detail, name='transfer_listing_detail'),
    path('create/', views.create_transfer_listing, name='create_transfer_listing'),
    path('club/', views.club_transfers, name='club_transfers'),
    path('listing/<int:listing_id>/cancel/', views.cancel_transfer_listing, name='cancel_transfer_listing'),
    path('offer/<int:offer_id>/cancel/', views.cancel_transfer_offer, name='cancel_transfer_offer'),
    path('offer/<int:offer_id>/accept/', views.accept_transfer_offer, name='accept_transfer_offer'),
    path('offer/<int:offer_id>/reject/', views.reject_transfer_offer, name='reject_transfer_offer'),
    path('history/', views.transfer_history, name='transfer_history'),
    path('api/expire-listing/<int:listing_id>/', views.expire_transfer_listing, name='expire_transfer_listing'),
    path('api/listing-info/<int:listing_id>/', views.get_listing_info, name='get_listing_info'),
]
