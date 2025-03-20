from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

from players.models import Player
from clubs.models import Club
from tournaments.models import Season

class TransferListing(models.Model):
    """
    Модель для выставления игрока на трансферный рынок
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transfer_listings')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='transfer_listings')
    asking_price = models.PositiveIntegerField()
    listed_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-listed_at']
        verbose_name = 'Transfer Listing'
        verbose_name_plural = 'Transfer Listings'
    
    def __str__(self):
        return f"{self.player.full_name} - {self.asking_price} tokens"
    
    def cancel(self):
        """
        Отменяет трансферный листинг и все связанные предложения
        """
        self.status = 'cancelled'
        self.save()
        
        # Отменяем все ожидающие предложения
        self.offers.filter(status='pending').update(status='cancelled')
        
        return True
    
    def complete(self):
        """
        Помечает трансферный листинг как завершенный
        """
        self.status = 'completed'
        self.save()
        
        # Отклоняем все остальные ожидающие предложения
        self.offers.filter(status='pending').update(status='rejected')
        
        return True

class TransferOffer(models.Model):
    """
    Модель для предложений по трансферу
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    transfer_listing = models.ForeignKey(TransferListing, on_delete=models.CASCADE, related_name='offers')
    bidding_club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='transfer_offers')
    bid_amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-bid_amount', '-created_at']
        verbose_name = 'Transfer Offer'
        verbose_name_plural = 'Transfer Offers'
    
    def __str__(self):
        return f"{self.bidding_club.name} - {self.bid_amount} tokens for {self.transfer_listing.player.full_name}"
    
    def accept(self):
        """
        Принимает предложение и выполняет трансфер
        """
        # Проверяем, что предложение и листинг активны
        if self.status != 'pending' or self.transfer_listing.status != 'active':
            return False
        
        # Проверяем, что у покупателя достаточно токенов
        buyer = self.bidding_club.owner
        if not buyer or buyer.tokens < self.bid_amount:
            return False
        
        # Получаем продавца
        seller = self.transfer_listing.club.owner
        if not seller:
            return False
        
        # Выполняем финансовую транзакцию
        buyer.tokens -= self.bid_amount
        seller.tokens += self.bid_amount
        buyer.save()
        seller.save()
        
        # Обновляем клуб игрока
        player = self.transfer_listing.player
        old_club = player.club
        player.club = self.bidding_club
        player.save()
        
        # Обновляем статусы
        self.status = 'accepted'
        self.save()
        self.transfer_listing.complete()
        
        # Создаем запись в истории трансферов
        try:
            current_season = Season.objects.filter(is_active=True).first()
        except:
            current_season = None
            
        TransferHistory.objects.create(
            player=player,
            from_club=old_club,
            to_club=self.bidding_club,
            transfer_fee=self.bid_amount,
            season=current_season
        )
        
        return True
    
    def reject(self):
        """
        Отклоняет предложение
        """
        self.status = 'rejected'
        self.save()
        return True
    
    def cancel(self):
        """
        Отменяет предложение
        """
        self.status = 'cancelled'
        self.save()
        return True

class TransferHistory(models.Model):
    """
    Модель для истории трансферов
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transfer_history')
    from_club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='transfers_out')
    to_club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='transfers_in')
    transfer_fee = models.PositiveIntegerField()
    transfer_date = models.DateTimeField(default=timezone.now)
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers')
    
    class Meta:
        ordering = ['-transfer_date']
        verbose_name = 'Transfer History'
        verbose_name_plural = 'Transfer History'
    
    def __str__(self):
        return f"{self.player.full_name}: {self.from_club.name} → {self.to_club.name} ({self.transfer_fee} tokens)"
