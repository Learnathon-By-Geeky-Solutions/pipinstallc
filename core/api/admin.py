from django.contrib import admin

# Register your models here.

from .models import Contributions, ContributionTags, contributionVideos, ContributionNotes, Enrollment, ContributionsComments, ContributionRatings

admin.site.register(Contributions)
admin.site.register(ContributionTags)
admin.site.register(contributionVideos)
admin.site.register(ContributionNotes)
admin.site.register(Enrollment)
admin.site.register(ContributionsComments)


admin.site.register(ContributionRatings)