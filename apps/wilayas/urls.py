from django.urls import path
from .views import load_communes


app_name = "wilayas"


urlpatterns = [
    path("load_communes/", load_communes, name="load_communes"),
]
