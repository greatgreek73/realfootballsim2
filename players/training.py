from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class TrainingSettings(models.Model):
    """Настройки тренировок для индивидуального игрока."""
    
    player = models.OneToOneField(
        'players.Player',
        on_delete=models.CASCADE,
        related_name='training_settings',
        verbose_name="Player"
    )
    
    # === Настройки для полевых игроков ===
    physical_weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=Decimal('16.67'),  # 100/6 = ~16.67% по умолчанию для равномерного распределения
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Physical Training Weight (%)",
        help_text="Процент фокуса на физические характеристики (strength, stamina, pace)"
    )
    
    defensive_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('16.67'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Defensive Training Weight (%)",
        help_text="Процент фокуса на защитные характеристики (marking, tackling, heading)"
    )
    
    attacking_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('16.67'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Attacking Training Weight (%)",
        help_text="Процент фокуса на атакующие характеристики (finishing, heading, long_range)"
    )
    
    mental_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('16.67'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Mental Training Weight (%)",
        help_text="Процент фокуса на ментальные характеристики (vision, flair)"
    )
    
    technical_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('16.67'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Technical Training Weight (%)",
        help_text="Процент фокуса на технические характеристики (dribbling, crossing, passing)"
    )
    
    tactical_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('16.67'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Tactical Training Weight (%)",
        help_text="Процент фокуса на тактические характеристики (work_rate, positioning, accuracy)"
    )
    
    # === Настройки для вратарей ===
    gk_physical_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('33.33'),  # 100/3 для вратарей
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="GK Physical Training Weight (%)",
        help_text="Процент фокуса на физические характеристики для вратарей"
    )
    
    gk_core_skills_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('33.33'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="GK Core Skills Weight (%)",
        help_text="Процент фокуса на основные навыки вратаря (reflexes, handling, positioning, aerial)"
    )
    
    gk_additional_skills_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('33.34'),  # Остаток для точности в 100%
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="GK Additional Skills Weight (%)",
        help_text="Процент фокуса на дополнительные навыки вратаря (command, distribution, etc.)"
    )
    
    # === Метаданные ===
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        verbose_name = 'Training Settings'
        verbose_name_plural = 'Training Settings'
        
    def __str__(self):
        return f"Training settings for {self.player.full_name}"
    
    def clean(self):
        """Проверяет, что сумма процентов равна 100%."""
        from django.core.exceptions import ValidationError
        
        if self.player.is_goalkeeper:
            # Проверка для вратаря
            total = (self.gk_physical_weight + 
                    self.gk_core_skills_weight + 
                    self.gk_additional_skills_weight)
            
            if abs(total - 100) > 0.01:  # Допускаем небольшую погрешность для Decimal
                raise ValidationError(
                    f'Сумма процентов для вратаря должна равняться 100%. '
                    f'Текущая сумма: {total}%'
                )
        else:
            # Проверка для полевого игрока
            total = (self.physical_weight + self.defensive_weight + 
                    self.attacking_weight + self.mental_weight + 
                    self.technical_weight + self.tactical_weight)
            
            if abs(total - 100) > 0.01:  # Допускаем небольшую погрешность для Decimal
                raise ValidationError(
                    f'Сумма процентов для полевого игрока должна равняться 100%. '
                    f'Текущая сумма: {total}%'
                )
    
    def get_field_player_weights(self):
        """Возвращает словарь весов для полевого игрока."""
        return {
            'physical': float(self.physical_weight) / 100,
            'defensive': float(self.defensive_weight) / 100,
            'attacking': float(self.attacking_weight) / 100,
            'mental': float(self.mental_weight) / 100,
            'technical': float(self.technical_weight) / 100,
            'tactical': float(self.tactical_weight) / 100,
        }
    
    def get_goalkeeper_weights(self):
        """Возвращает словарь весов для вратаря."""
        return {
            'physical': float(self.gk_physical_weight) / 100,
            'core_gk_skills': float(self.gk_core_skills_weight) / 100,
            'additional_gk_skills': float(self.gk_additional_skills_weight) / 100,
        }