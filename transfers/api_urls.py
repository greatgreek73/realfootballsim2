from django.urls import path

from . import api_views

app_name = "transfers_api"

# listings endpoint supports GET (list) and POST (create)
urlpatterns = [
    path("listings/", api_views.transfer_listings_list, name="listings-list"),
    path("listings/<int:listing_id>/", api_views.transfer_listing_detail, name="listings-detail"),
    path("listings/<int:listing_id>/cancel/", api_views.transfer_listing_cancel, name="listings-cancel"),
    path("listings/<int:listing_id>/expire/", api_views.transfer_listing_expire, name="listings-expire"),
    path("listings/<int:listing_id>/offers/", api_views.transfer_offer_create, name="offers-create"),
    path("offers/<int:offer_id>/cancel/", api_views.transfer_offer_cancel, name="offers-cancel"),
    path("offers/<int:offer_id>/reject/", api_views.transfer_offer_reject, name="offers-reject"),
    path("offers/<int:offer_id>/accept/", api_views.transfer_offer_accept, name="offers-accept"),
    path("history/", api_views.transfer_history_list, name="history-list"),
]
