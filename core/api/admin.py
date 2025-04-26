from django.contrib import admin

# Register your models here.

from .models import Contribution, ContributionTags, ContributionOrigines, ContributionVideos, ContributionNotes, Enrollment, ContributionComments, ContributionRatings

admin.site.register(Contribution)
admin.site.register(ContributionTags)
admin.site.register(ContributionOrigines)
admin.site.register(ContributionVideos)
admin.site.register(ContributionNotes)
admin.site.register(Enrollment)
admin.site.register(ContributionComments)


admin.site.register(ContributionRatings)