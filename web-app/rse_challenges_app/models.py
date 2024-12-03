from django.db import models


class Challenge(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_date = models.DateTimeField("Date Created")
    last_modified_date = models.DateTimeField("Date Last Modified")
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    evidence_text = models.TextField()
    impacts_text = models.TextField()
    objectives_text = models.TextField()
    actions_and_outputs_text = models.TextField()
    active_projects_text = models.TextField()
    past_work_text = models.TextField()


class Resource(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField()
