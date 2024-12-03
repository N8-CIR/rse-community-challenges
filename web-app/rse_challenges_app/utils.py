import markdown
from .models import Challenge


def create_challenge_context(challenge: Challenge):
    return {
        **challenge.__dict__,
        "likes": 999,
        "name": challenge.name,
        "description": markdown.markdown(challenge.description),
        "created_date": challenge.created_date,
        "last_modified_date": challenge.last_modified_date,
        "is_active": challenge.is_active,
        "is_deleted": challenge.is_deleted,
        "evidence_text": markdown.markdown(challenge.evidence_text),
        "impacts_text": markdown.markdown(challenge.impacts_text),
        "objectives_text": markdown.markdown(challenge.objectives_text),
        "actions_and_outputs_text": markdown.markdown(
            challenge.actions_and_outputs_text, extensions=["tables"]
        ),
        "active_projects_text": markdown.markdown(challenge.active_projects_text),
        "past_work_text": markdown.markdown(challenge.past_work_text),
    }
