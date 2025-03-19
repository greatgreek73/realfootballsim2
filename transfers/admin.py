from django.contrib import admin
from .models import TransferListing, TransferOffer, TransferHistory

@admin.register(TransferListing)
class TransferListingAdmin(admin.ModelAdmin):
    list_display = ('player', 'club', 'asking_price', 'listed_at', 'status')
    list_filter = ('status', 'club')
    search_fields = ('player__first_name', 'player__last_name', 'club__name')
    date_hierarchy = 'listed_at'
    readonly_fields = ('listed_at',)

@admin.register(TransferOffer)
class TransferOfferAdmin(admin.ModelAdmin):
    list_display = ('transfer_listing', 'bidding_club', 'bid_amount', 'created_at', 'status')
    list_filter = ('status', 'bidding_club')
    search_fields = ('transfer_listing__player__first_name', 'transfer_listing__player__last_name', 'bidding_club__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

@admin.register(TransferHistory)
class TransferHistoryAdmin(admin.ModelAdmin):
    list_display = ('player', 'from_club', 'to_club', 'transfer_fee', 'transfer_date', 'season')
    list_filter = ('season', 'from_club', 'to_club')
    search_fields = ('player__first_name', 'player__last_name', 'from_club__name', 'to_club__name')
    date_hierarchy = 'transfer_date'
    readonly_fields = ('transfer_date',)
