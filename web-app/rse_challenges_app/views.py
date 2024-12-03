from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .models import Challenge
from .utils import create_challenge_context


def index(request: HttpRequest) -> HttpResponse:
    """Homepage view."""
    challenges = Challenge.objects.all()
    context = {
        "challenges": challenges,
    }
    return render(request=request, template_name="index.html", context=context)


def challenge_view(request: HttpRequest, challenge_id: int) -> HttpResponse:
    """Default view of a challenge."""
    challenge = Challenge.objects.get(pk=challenge_id)

    context = {"challenge": create_challenge_context(challenge), "nav": "description"}
    return render(request=request, template_name="challenge.html", context=context)


def challenge_component_view(
    request: HttpRequest, challenge_id: int, component_key: str
) -> HttpResponse:
    """View of a challenge section."""
    challenge = Challenge.objects.get(pk=challenge_id)

    context = {"challenge": create_challenge_context(challenge), "nav": component_key}

    component_templates = {
        "description": "challenge/challenge_description.html",
        "evidence": "challenge/challenge_evidence.html",
        "impacts": "challenge/challenge_impacts.html",
        "objectives": "challenge/challenge_objectives.html",
        "actions_and_outputs": "challenge/challenge_actions_and_outputs.html",
        "active_projects": "challenge/challenge_active_projects.html",
        "past_work": "challenge/challenge_past_work.html",
        "resources": "challenge/challenge_resources.html",
    }
    template = component_templates.get(component_key, "404.html")
    return render(request=request, template_name=template, context=context)
