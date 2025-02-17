from django.contrib import admin

from .models import (
    Resource,
    Evidence,
    Impact,
    Objective,
    Output,
    Action,
    Input,
    Challenge,
)


admin.site.register(Resource)
admin.site.register(Evidence)
admin.site.register(Impact)
admin.site.register(Objective)
admin.site.register(Output)
admin.site.register(Action)
admin.site.register(Input)
admin.site.register(Challenge)
