from django.contrib import admin

# Register your models here.

from .models import Contributions, ContributionTags, contributionVideos, ContributionNotes, ContributionsComments, ContributionRatings,University,Department,MajorSubject

admin.site.register(Contributions)
admin.site.register(ContributionTags)
admin.site.register(contributionVideos)
admin.site.register(ContributionNotes)
admin.site.register(ContributionsComments)
admin.site.register(University)
admin.site.register(Department)
admin.site.register(MajorSubject)
admin.site.register(ContributionRatings)