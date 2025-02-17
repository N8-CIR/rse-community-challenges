from django.test import TestCase, Client
from pytest_django.asserts import assertTemplateUsed
from rse_challenges_app.models import Challenge


class TestChallengeView(TestCase):
    """Test the challenge view."""

    fixtures = ["rse_challenges_app/fixtures/challenges.json"]

    def test_challenge_view(self):
        """Test viewing a challenge."""
        client = Client()
        with assertTemplateUsed(template_name="challenge.html"):  # type: ignore
            response = client.get("/app/challenge/1/")
        assert response.status_code == 200

    def test_challenge_view_shows_description(self):
        """Test that the challenge view shows the description."""
        client = Client()
        response = client.get("/app/challenge/1/")
        challenge_data = Challenge.objects.get(pk=1)
        assert challenge_data.name in response.content.decode()

    def test_challenge_component_view(self):
        """Test viewing a challenge component."""
        client = Client()
        with assertTemplateUsed(template_name="challenge/challenge_evidence.html"):  # type: ignore
            response = client.get("/app/challenge/1/evidence/")
        assert response.status_code == 200

    def test_challenge_view_shows_evidence(self):
        """Test that the challenge view shows the evidence."""
        client = Client()
        response = client.get("/app/challenge/1/evidence/")
        challenge_data = Challenge.objects.get(pk=1)
        assert challenge_data.evidences.all()[0].name in response.content.decode()
