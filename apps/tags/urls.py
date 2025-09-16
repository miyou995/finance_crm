from django.urls import path

from apps.tags.views import TagsListView,ManageSalleHtmx,SalleDeleteHTMX

app_name = "tags"


urlpatterns = [
    path("tags/", TagsListView.as_view(), name="list_tags"),
    path("tags/create/", ManageSalleHtmx.as_view(), name="create_tags"),
    path("tags/<int:pk>/", ManageSalleHtmx.as_view(), name="update_tags"),
    path("tags/<int:pk>/delete/", SalleDeleteHTMX.as_view(), name="delete_tags"),
]
