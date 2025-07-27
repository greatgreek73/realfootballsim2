from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from players.models import Player
from matches.models import PlayerRivalry, TeamChemistry, CharacterEvolution, NarrativeEvent
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Displays comprehensive narrative profile for a player'

    def add_arguments(self, parser):
        parser.add_argument(
            'player_id',
            type=int,
            help='ID of the player to analyze'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed evolution history and narrative events',
        )

    def handle(self, *args, **options):
        player_id = options['player_id']
        detailed = options.get('detailed', False)
        
        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            raise CommandError(f'Player with ID {player_id} does not exist.')

        self.stdout.write("\n" + "="*80)
        self.stdout.write(f"NARRATIVE PROFILE: {player.full_name}".center(80))
        self.stdout.write("="*80)
        
        # Basic Info
        self.display_basic_info(player)
        
        # Personality Traits
        self.display_personality(player)
        
        # Rivalries
        self.display_rivalries(player)
        
        # Team Chemistry
        self.display_team_chemistry(player)
        
        # Character Evolution
        self.display_character_evolution(player, detailed)
        
        # Narrative Events
        if detailed:
            self.display_narrative_events(player)
        
        # Summary Statistics
        self.display_summary_stats(player)
        
        self.stdout.write("\n" + "="*80)

    def display_basic_info(self, player):
        """Displays basic player information"""
        self.stdout.write(f"\nBASIC INFORMATION")
        self.stdout.write("-" * 40)
        self.stdout.write(f"Name: {player.full_name}")
        self.stdout.write(f"Club: {player.club.name if player.club else 'Free Agent'}")
        self.stdout.write(f"Position: {player.position}")
        self.stdout.write(f"Age: {player.age}")
        self.stdout.write(f"Overall Rating: {player.overall_rating}")

    def display_personality(self, player):
        """Displays personality traits"""
        self.stdout.write(f"\n[TRAITS] PERSONALITY TRAITS")
        self.stdout.write("-" * 40)
        
        if not player.personality_traits:
            self.stdout.write("No personality traits defined")
            return
            
        # Sort traits by value for better readability
        sorted_traits = sorted(
            player.personality_traits.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for trait, value in sorted_traits:
            # Create visual bar
            bar_length = int(value / 5)  # Scale 0-100 to 0-20
            bar = "#" * bar_length + "-" * (20 - bar_length)
            
            self.stdout.write(f"{trait.capitalize():>12}: {bar} {value:>3}/100")

    def display_rivalries(self, player):
        """Displays player rivalries"""
        self.stdout.write(f"\n[RIVALRIES]  RIVALRIES")
        self.stdout.write("-" * 40)
        
        rivalries = PlayerRivalry.objects.filter(
            Q(player1=player) | Q(player2=player)
        ).order_by('-intensity', '-interaction_count')
        
        if not rivalries.exists():
            self.stdout.write("No rivalries found")
            return
            
        for rivalry in rivalries:
            # Determine opponent
            opponent = rivalry.player2 if rivalry.player1 == player else rivalry.player1
            
            # Format intensity with symbols
            intensity_symbols = {
                'mild': '*',
                'moderate': '**',
                'strong': '***',
                'intense': '****'
            }
            
            intensity_display = intensity_symbols.get(rivalry.intensity, '?')
            
            self.stdout.write(f"\nOpponent: {opponent.full_name}")
            self.stdout.write(f"  Type: {rivalry.get_rivalry_type_display()}")
            self.stdout.write(f"  Intensity: {rivalry.get_intensity_display()} {intensity_display}")
            self.stdout.write(f"  Interactions: {rivalry.interaction_count}")
            self.stdout.write(f"  Created: {rivalry.created_date}")
            self.stdout.write(f"  Last Interaction: {rivalry.last_interaction or 'Never'}")
            self.stdout.write(f"  Game Effects:")
            self.stdout.write(f"    Aggression Modifier: {rivalry.aggression_modifier:+.2f}")
            self.stdout.write(f"    Performance Modifier: {rivalry.performance_modifier:+.2f}")

    def display_team_chemistry(self, player):
        """Displays team chemistry relationships"""
        self.stdout.write(f"\n[CHEMISTRY] TEAM CHEMISTRY")
        self.stdout.write("-" * 40)
        
        chemistry_bonds = TeamChemistry.objects.filter(
            Q(player1=player) | Q(player2=player)
        ).order_by('-strength', '-positive_interactions')
        
        if not chemistry_bonds.exists():
            self.stdout.write("No chemistry bonds found")
            return
            
        for chemistry in chemistry_bonds:
            # Determine partner
            partner = chemistry.player2 if chemistry.player1 == player else chemistry.player1
            
            # Format strength with bars
            strength_percentage = int(chemistry.strength * 100)
            hearts = int(chemistry.strength * 5)
            heart_display = "#" * hearts + "-" * (5 - hearts)
            
            self.stdout.write(f"\nPartner: {partner.full_name}")
            self.stdout.write(f"  Type: {chemistry.get_chemistry_type_display()}")
            self.stdout.write(f"  Strength: {strength_percentage}% {heart_display}")
            self.stdout.write(f"  Positive Interactions: {chemistry.positive_interactions}")
            self.stdout.write(f"  Created: {chemistry.created_date}")
            self.stdout.write(f"  Last Positive: {chemistry.last_positive_interaction or 'Never'}")
            self.stdout.write(f"  Game Effects:")
            self.stdout.write(f"    Passing Bonus: +{chemistry.passing_bonus:.2f}")
            self.stdout.write(f"    Teamwork Bonus: +{chemistry.teamwork_bonus:.2f}")

    def display_character_evolution(self, player, detailed=False):
        """Displays character evolution history"""
        self.stdout.write(f"\n[EVOLUTION] CHARACTER EVOLUTION")
        self.stdout.write("-" * 40)
        
        evolutions = CharacterEvolution.objects.filter(
            player=player
        ).order_by('-timestamp')
        
        if not evolutions.exists():
            self.stdout.write("No character evolution recorded")
            return
            
        # Show summary first
        total_evolutions = evolutions.count()
        recent_evolutions = evolutions.filter(
            timestamp__gte=datetime.now() - timedelta(days=30)
        ).count()
        
        self.stdout.write(f"Total Evolutions: {total_evolutions}")
        self.stdout.write(f"Recent (30 days): {recent_evolutions}")
        
        # Group by trait for summary
        trait_changes = {}
        for evolution in evolutions:
            trait = evolution.trait_changed
            if trait not in trait_changes:
                trait_changes[trait] = {'total_change': 0, 'count': 0}
            trait_changes[trait]['total_change'] += evolution.change_amount
            trait_changes[trait]['count'] += 1
        
        if trait_changes:
            self.stdout.write(f"\nTrait Change Summary:")
            for trait, data in sorted(trait_changes.items()):
                avg_change = data['total_change'] / data['count']
                self.stdout.write(
                    f"  {trait.capitalize():>12}: "
                    f"{data['total_change']:+3} total, "
                    f"{avg_change:+.1f} avg ({data['count']} changes)"
                )
        
        if detailed:
            self.stdout.write(f"\nDetailed Evolution History:")
            for i, evolution in enumerate(evolutions[:20]):  # Show last 20
                trigger_icon = {
                    'goal_scored': '[GOAL]',
                    'match_won': '[WIN]',
                    'match_lost': '[LOSS]',
                    'rivalry_interaction': '[RIVAL]',
                    'team_chemistry': '[CHEM]',
                    'injury': '[INJ]',
                    'transfer': '[TRF]',
                    'captain_appointment': '[CAP]'
                }.get(evolution.trigger_event, '[EVT]')
                
                self.stdout.write(
                    f"  {i+1:2}. {trigger_icon} {evolution.trigger_event.replace('_', ' ').title()}"
                )
                self.stdout.write(
                    f"      {evolution.trait_changed}: "
                    f"{evolution.old_value} -> {evolution.new_value} "
                    f"({evolution.change_amount:+})"
                )
                self.stdout.write(f"      {evolution.timestamp.strftime('%Y-%m-%d %H:%M')}")
                if evolution.match:
                    self.stdout.write(f"      Match: {evolution.match}")

    def display_narrative_events(self, player):
        """Displays narrative events involving the player"""
        self.stdout.write(f"\n[EVENTS] NARRATIVE EVENTS")
        self.stdout.write("-" * 40)
        
        # Events where player is primary
        primary_events = NarrativeEvent.objects.filter(
            primary_player=player
        ).order_by('-timestamp')[:10]
        
        # Events where player is secondary
        secondary_events = NarrativeEvent.objects.filter(
            secondary_player=player
        ).order_by('-timestamp')[:10]
        
        all_events = list(primary_events) + list(secondary_events)
        all_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        if not all_events:
            self.stdout.write("No narrative events found")
            return
            
        importance_icons = {
            'minor': '[MIN]',
            'significant': '[SIG]',
            'major': '[MAJ]',
            'legendary': '[LEG]'
        }
        
        for i, event in enumerate(all_events[:15]):  # Show last 15
            icon = importance_icons.get(event.importance, '[EVT]')
            role = "Primary" if event.primary_player == player else "Secondary"
            
            self.stdout.write(f"\n{i+1:2}. {icon} {event.title}")
            self.stdout.write(f"    Role: {role}")
            self.stdout.write(f"    Type: {event.get_event_type_display()}")
            self.stdout.write(f"    Importance: {event.get_importance_display()}")
            self.stdout.write(f"    Match: {event.match}")
            self.stdout.write(f"    Minute: {event.minute}")
            self.stdout.write(f"    Date: {event.timestamp.strftime('%Y-%m-%d %H:%M')}")
            
            # Show description if not too long
            if len(event.description) <= 100:
                self.stdout.write(f"    \"{event.description}\"")

    def display_summary_stats(self, player):
        """Displays summary statistics"""
        self.stdout.write(f"\n[STATS] NARRATIVE STATISTICS")
        self.stdout.write("-" * 40)
        
        # Count various narrative elements
        rivalry_count = PlayerRivalry.objects.filter(
            Q(player1=player) | Q(player2=player)
        ).count()
        
        chemistry_count = TeamChemistry.objects.filter(
            Q(player1=player) | Q(player2=player)
        ).count()
        
        evolution_count = CharacterEvolution.objects.filter(player=player).count()
        
        narrative_count = NarrativeEvent.objects.filter(
            Q(primary_player=player) | Q(secondary_player=player)
        ).count()
        
        # Calculate narrative activity level
        total_narrative_elements = rivalry_count + chemistry_count + evolution_count + narrative_count
        
        if total_narrative_elements == 0:
            activity_level = "Inactive"
        elif total_narrative_elements < 5:
            activity_level = "Low"
        elif total_narrative_elements < 15:
            activity_level = "Moderate" 
        elif total_narrative_elements < 30:
            activity_level = "High"
        else:
            activity_level = "Very High"
        
        self.stdout.write(f"Rivalries: {rivalry_count}")
        self.stdout.write(f"Chemistry Bonds: {chemistry_count}")
        self.stdout.write(f"Character Evolutions: {evolution_count}")
        self.stdout.write(f"Narrative Events: {narrative_count}")
        self.stdout.write(f"Total Narrative Elements: {total_narrative_elements}")
        self.stdout.write(f"Narrative Activity Level: {activity_level}")
        
        # Calculate most changed personality trait
        if evolution_count > 0:
            trait_changes = {}
            evolutions = CharacterEvolution.objects.filter(player=player)
            
            for evolution in evolutions:
                trait = evolution.trait_changed
                if trait not in trait_changes:
                    trait_changes[trait] = 0
                trait_changes[trait] += abs(evolution.change_amount)
            
            if trait_changes:
                most_changed_trait = max(trait_changes, key=trait_changes.get)
                self.stdout.write(f"Most Evolving Trait: {most_changed_trait.capitalize()} ({trait_changes[most_changed_trait]} total change)")