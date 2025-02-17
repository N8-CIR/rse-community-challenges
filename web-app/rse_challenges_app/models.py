from django.db import models


class Resource(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField()


class Evidence(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()


class Impact(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    evidences = models.ManyToManyField(Evidence)


class Objective(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    impacts = models.ManyToManyField(Impact)


class Output(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    objectives = models.ManyToManyField(Objective)


class Action(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    outputs = models.ManyToManyField(Output)
    status = models.CharField(max_length=200)


class Input(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    actions = models.ManyToManyField(Action)


class Challenge(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_date = models.DateTimeField("Date Created")
    last_modified_date = models.DateTimeField("Date Last Modified")
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    inputs = models.ManyToManyField(Input)
    actions = models.ManyToManyField(Action)
    outputs = models.ManyToManyField(Output)
    objectives = models.ManyToManyField(Objective)
    impacts = models.ManyToManyField(Impact)
    evidences = models.ManyToManyField(Evidence)
    resources = models.ManyToManyField(Resource)
