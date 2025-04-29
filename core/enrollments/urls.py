from django.urls import path
from .views import (
    EnrollmentView,CreateEnrollmentView,
    payment_success, payment_fail, payment_cancel
)

urlpatterns = [

    # user can view their enrollments and create new enrollments
    path('enrollments/', EnrollmentView.as_view(), name='user-enrollments'),
    path('enrollments/<uuid:enrollment_id>/', EnrollmentView.as_view(), name='enrollment-detail'),
    path('create-enrollments/<uuid:contribution_id>/', CreateEnrollmentView.as_view(), name='enrollment-detail'),

    # payment urls
    path('payment/success/<uuid:enrollment_id>/', payment_success, name='payment_success'),
    path('payment/fail/<uuid:enrollment_id>/', payment_fail, name='payment_fail'),
    path('payment/cancel/<uuid:enrollment_id>/', payment_cancel, name='payment_cancel'),

   
]

