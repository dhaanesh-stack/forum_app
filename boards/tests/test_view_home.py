from django.urls import reverse, resolve
from django.test import TestCase
from boards.views import home
from ..models import Board
from django.contrib.auth.models import User


class HomeTests(TestCase):
    

    def setUp(self):
        self.board = Board.objects.create(name="Django", description="Django board.")
        url = reverse("home")
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve("/")
        self.assertEqual(view.func, home)

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse("board_topics", kwargs={"pk": self.board.pk})
        self.assertContains(self.response, f'href="{board_topics_url}"')
    def test_home_view_status_code(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve("/")
        self.assertEqual(view.func, home)


