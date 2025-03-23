from django import forms
from .models import TransferListing, TransferOffer
from players.models import Player

class TransferListingForm(forms.ModelForm):
    """
    Форма для выставления игрока на трансфер
    """
    class Meta:
        model = TransferListing
        fields = ['player', 'asking_price', 'duration', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'duration': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.club = kwargs.pop('club', None)
        super().__init__(*args, **kwargs)
        
        if self.club:
            # Ограничиваем выбор игроков только игроками данного клуба
            self.fields['player'].queryset = Player.objects.filter(club=self.club)
            
            # Устанавливаем минимальную цену для каждого игрока
            self.fields['player'].widget.attrs.update({
                'class': 'player-select',
                'data-min-price': True
            })
        
        # Добавляем подсказки для полей
        self.fields['duration'].help_text = 'Выберите длительность трансфера'
        self.fields['asking_price'].help_text = 'Начальная цена аукциона в монетах'
    
    def clean(self):
        cleaned_data = super().clean()
        player = cleaned_data.get('player')
        asking_price = cleaned_data.get('asking_price')
        
        if player and asking_price:
            min_price = player.get_purchase_cost()
            if asking_price < min_price:
                self.add_error('asking_price', 
                    f'Asking price cannot be lower than player\'s base value ({min_price} монет)')
        
        return cleaned_data


class TransferOfferForm(forms.ModelForm):
    """
    Форма для создания предложения по трансферу
    """
    class Meta:
        model = TransferOffer
        fields = ['bid_amount', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.transfer_listing = kwargs.pop('transfer_listing', None)
        self.bidding_club = kwargs.pop('bidding_club', None)
        super().__init__(*args, **kwargs)
        
        if self.transfer_listing:
            # Устанавливаем минимальную цену предложения равной запрашиваемой цене
            self.fields['bid_amount'].min_value = self.transfer_listing.asking_price
            self.fields['bid_amount'].initial = self.transfer_listing.asking_price
            self.fields['bid_amount'].help_text = f'Minimum: {self.transfer_listing.asking_price} монет'
    
    def clean(self):
        cleaned_data = super().clean()
        bid_amount = cleaned_data.get('bid_amount')
        
        if not self.transfer_listing or not self.bidding_club:
            raise forms.ValidationError("Missing transfer listing or bidding club")
        
        if bid_amount:
            # Проверка, что предложение не ниже запрашиваемой цены
            if bid_amount < self.transfer_listing.asking_price:
                self.add_error('bid_amount', 
                    f'Bid amount cannot be lower than asking price ({self.transfer_listing.asking_price} монет)')
            
            # Проверка, что у клуба-покупателя достаточно денег
            if self.bidding_club.owner and self.bidding_club.owner.money < bid_amount:
                self.add_error('bid_amount', 
                    f'You do not have enough money. Available: {self.bidding_club.owner.money} монет')
        
        return cleaned_data
