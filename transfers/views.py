from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.db.models import Q

from .models import TransferListing, TransferOffer, TransferHistory
from .forms import TransferListingForm, TransferOfferForm
from clubs.models import Club
from players.models import Player

@login_required
def transfer_market(request):
    """
    Отображает трансферный рынок со всеми активными листингами
    """
    # Получаем все активные листинги
    listings = TransferListing.objects.filter(status='active')
    
    # Фильтрация по позиции, если указана
    position = request.GET.get('position')
    if position:
        listings = listings.filter(player__position=position)
    
    # Фильтрация по возрасту, если указан диапазон
    min_age = request.GET.get('min_age')
    max_age = request.GET.get('max_age')
    if min_age:
        listings = listings.filter(player__age__gte=min_age)
    if max_age:
        listings = listings.filter(player__age__lte=max_age)
    
    # Фильтрация по цене, если указан диапазон
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        listings = listings.filter(asking_price__gte=min_price)
    if max_price:
        listings = listings.filter(asking_price__lte=max_price)
    
    # Получаем клуб пользователя, если есть
    user_club = None
    try:
        user_club = request.user.club
    except:
        pass
    
    context = {
        'listings': listings,
        'user_club': user_club,
        'positions': Player.POSITIONS,
        'filters': {
            'position': position,
            'min_age': min_age,
            'max_age': max_age,
            'min_price': min_price,
            'max_price': max_price,
        }
    }
    
    return render(request, 'transfers/transfer_market.html', context)

@login_required
def transfer_listing_detail(request, listing_id):
    """
    Отображает детальную информацию о листинге и форму для создания предложения
    """
    listing = get_object_or_404(TransferListing, id=listing_id)
    
    # Проверяем, есть ли у пользователя клуб
    try:
        user_club = request.user.club
    except:
        user_club = None
    
    # Проверяем, не является ли пользователь владельцем клуба-продавца
    is_seller = user_club == listing.club if user_club else False
    
    # Получаем предложения пользователя по этому листингу, если он не продавец
    user_offers = []
    if user_club and not is_seller:
        user_offers = TransferOffer.objects.filter(
            transfer_listing=listing,
            bidding_club=user_club
        )
    
    # Если пользователь - продавец, получаем все предложения по этому листингу
    all_offers = []
    if is_seller:
        all_offers = TransferOffer.objects.filter(
            transfer_listing=listing,
            status='pending'
        )
    
    # Создаем форму для нового предложения, если пользователь не продавец
    form = None
    if user_club and not is_seller and listing.status == 'active':
        if request.method == 'POST':
            form = TransferOfferForm(
                request.POST,
                transfer_listing=listing,
                bidding_club=user_club
            )
            if form.is_valid():
                offer = form.save(commit=False)
                offer.transfer_listing = listing
                offer.bidding_club = user_club
                offer.save()
                messages.success(request, 'Your offer has been submitted.')
                return redirect('transfer_listing_detail', listing_id=listing.id)
        else:
            form = TransferOfferForm(
                transfer_listing=listing,
                bidding_club=user_club
            )
    
    context = {
        'listing': listing,
        'user_club': user_club,
        'is_seller': is_seller,
        'user_offers': user_offers,
        'all_offers': all_offers,
        'form': form,
    }
    
    return render(request, 'transfers/transfer_listing_detail.html', context)

@login_required
def create_transfer_listing(request):
    """
    Создает новый трансферный листинг
    """
    # Проверяем, есть ли у пользователя клуб
    try:
        user_club = request.user.club
    except:
        messages.error(request, 'You need to have a club to list players for transfer.')
        return redirect('transfer_market')
    
    if request.method == 'POST':
        form = TransferListingForm(request.POST, club=user_club)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.club = user_club
            listing.save()
            messages.success(request, f'{listing.player.full_name} has been listed on the transfer market.')
            return redirect('transfers:club_transfers')
    else:
        form = TransferListingForm(club=user_club)
    
    context = {
        'form': form,
        'club': user_club,
    }
    
    return render(request, 'transfers/create_transfer_listing.html', context)

@login_required
def club_transfers(request):
    """
    Отображает страницу управления трансферами клуба
    """
    # Проверяем, есть ли у пользователя клуб
    try:
        user_club = request.user.club
    except:
        messages.error(request, 'You need to have a club to manage transfers.')
        return redirect('transfer_market')
    
    # Получаем активные листинги клуба
    active_listings = TransferListing.objects.filter(
        club=user_club,
        status='active'
    )
    
    # Получаем игроков клуба, которые не выставлены на трансфер
    players_not_listed = Player.objects.filter(
        club=user_club
    ).exclude(
        id__in=active_listings.values_list('player__id', flat=True)
    )
    
    # Получаем предложения по активным листингам клуба
    pending_offers = TransferOffer.objects.filter(
        transfer_listing__club=user_club,
        transfer_listing__status='active',
        status='pending'
    )
    
    # Получаем историю трансферов клуба
    transfer_history = TransferHistory.objects.filter(
        Q(from_club=user_club) | Q(to_club=user_club)
    )
    
    context = {
        'club': user_club,
        'active_listings': active_listings,
        'players_not_listed': players_not_listed,
        'pending_offers': pending_offers,
        'transfer_history': transfer_history,
    }
    
    return render(request, 'transfers/club_transfers.html', context)

@login_required
def cancel_transfer_listing(request, listing_id):
    """
    Отменяет трансферный листинг
    """
    listing = get_object_or_404(TransferListing, id=listing_id)
    
    # Проверяем, является ли пользователь владельцем клуба-продавца
    try:
        user_club = request.user.club
    except:
        return HttpResponseForbidden("You don't have permission to cancel this listing.")
    
    if user_club != listing.club:
        return HttpResponseForbidden("You don't have permission to cancel this listing.")
    
    if listing.status != 'active':
        messages.error(request, 'This listing cannot be cancelled.')
        return redirect('club_transfers')
    
    listing.cancel()
    messages.success(request, f'Listing for {listing.player.full_name} has been cancelled.')
    return redirect('club_transfers')

@login_required
def cancel_transfer_offer(request, offer_id):
    """
    Отменяет предложение по трансферу
    """
    offer = get_object_or_404(TransferOffer, id=offer_id)
    
    # Проверяем, является ли пользователь владельцем клуба-покупателя
    try:
        user_club = request.user.club
    except:
        return HttpResponseForbidden("You don't have permission to cancel this offer.")
    
    if user_club != offer.bidding_club:
        return HttpResponseForbidden("You don't have permission to cancel this offer.")
    
    if offer.status != 'pending':
        messages.error(request, 'This offer cannot be cancelled.')
        return redirect('transfer_listing_detail', listing_id=offer.transfer_listing.id)
    
    offer.cancel()
    messages.success(request, 'Your offer has been cancelled.')
    return redirect('transfer_listing_detail', listing_id=offer.transfer_listing.id)

@login_required
def accept_transfer_offer(request, offer_id):
    """
    Принимает предложение по трансферу
    """
    offer = get_object_or_404(TransferOffer, id=offer_id)
    
    # Проверяем, является ли пользователь владельцем клуба-продавца
    try:
        user_club = request.user.club
    except:
        return HttpResponseForbidden("You don't have permission to accept this offer.")
    
    if user_club != offer.transfer_listing.club:
        return HttpResponseForbidden("You don't have permission to accept this offer.")
    
    if offer.status != 'pending' or offer.transfer_listing.status != 'active':
        messages.error(request, 'This offer cannot be accepted.')
        return redirect('club_transfers')
    
    # Принимаем предложение, что запускает процесс трансфера
    if offer.accept():
        messages.success(
            request, 
            f'Transfer completed! {offer.transfer_listing.player.full_name} has been transferred to {offer.bidding_club.name} for {offer.bid_amount} tokens.'
        )
    else:
        messages.error(request, 'There was an error processing the transfer.')
    
    return redirect('club_transfers')

@login_required
def reject_transfer_offer(request, offer_id):
    """
    Отклоняет предложение по трансферу
    """
    offer = get_object_or_404(TransferOffer, id=offer_id)
    
    # Проверяем, является ли пользователь владельцем клуба-продавца
    try:
        user_club = request.user.club
    except:
        return HttpResponseForbidden("You don't have permission to reject this offer.")
    
    if user_club != offer.transfer_listing.club:
        return HttpResponseForbidden("You don't have permission to reject this offer.")
    
    if offer.status != 'pending':
        messages.error(request, 'This offer cannot be rejected.')
        return redirect('club_transfers')
    
    offer.reject()
    messages.success(request, 'The offer has been rejected.')
    return redirect('club_transfers')

@login_required
def transfer_history(request):
    """
    Отображает историю всех трансферов
    """
    # Получаем все трансферы
    transfers = TransferHistory.objects.all()
    
    # Фильтрация по сезону, если указан
    season_id = request.GET.get('season')
    if season_id:
        transfers = transfers.filter(season_id=season_id)
    
    # Фильтрация по клубу, если указан
    club_id = request.GET.get('club')
    if club_id:
        transfers = transfers.filter(Q(from_club_id=club_id) | Q(to_club_id=club_id))
    
    # Фильтрация по игроку, если указан
    player_id = request.GET.get('player')
    if player_id:
        transfers = transfers.filter(player_id=player_id)
    
    context = {
        'transfers': transfers,
        'seasons': Season.objects.all(),
        'clubs': Club.objects.all(),
        'filters': {
            'season': season_id,
            'club': club_id,
            'player': player_id,
        }
    }
    
    return render(request, 'transfers/transfer_history.html', context)
