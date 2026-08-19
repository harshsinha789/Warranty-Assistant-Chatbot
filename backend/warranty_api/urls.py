from django.urls import path

from .views import check_warranty_api


urlpatterns = [
    path(
        "check-warranty/",
        check_warranty_api,
        name="check_warranty"
    ),
]