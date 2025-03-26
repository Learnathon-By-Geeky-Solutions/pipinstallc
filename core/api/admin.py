from django.contrib import admin

# Register your models here.

from .models import Contributions, Contribution_tags, Contribution_origines, contribution_videos, Contribution_notes, Enrollment, Contributions_comments

admin.site.register(Contributions)
admin.site.register(Contribution_tags)
admin.site.register(Contribution_origines)
admin.site.register(contribution_videos)
admin.site.register(Contribution_notes)
admin.site.register(Enrollment)
admin.site.register(Contributions_comments)


