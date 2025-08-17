from django.test import TestCase
from django.urls import reverse


class NamespaceTestCase(TestCase):
    def test_players_namespace(self):
        """Test that players namespace is registered"""
        url = reverse('players:player_detail', args=[1])
        self.assertEqual(url, '/players/detail/1/')
        
    def test_core_namespace(self):
        """Test core namespace"""
        url = reverse('core:home')
        self.assertEqual(url, '/')
        
    def test_clubs_namespace(self):
        """Test clubs namespace"""
        url = reverse('clubs:club_list')
        self.assertEqual(url, '/clubs/')
        
    def test_matches_namespace(self):
        """Test matches namespace"""
        url = reverse('matches:match_list')
        self.assertEqual(url, '/matches/')
        
    def test_tournaments_namespace(self):
        """Test tournaments namespace"""
        url = reverse('tournaments:championship_list')
        self.assertEqual(url, '/tournaments/')
        
    def test_transfers_namespace(self):
        """Test transfers namespace"""
        url = reverse('transfers:transfer_market')
        self.assertEqual(url, '/transfers/market/')
        
    def test_narrative_namespace(self):
        """Test narrative namespace"""
        url = reverse('narrative:story_center')
        self.assertEqual(url, '/narrative/story-center/')