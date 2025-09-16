import json
from django.http import HttpResponse
from django.shortcuts import render

from apps.wilayas.models import Commune

# Create your views here.


def load_communes(request):
    wilaya_id = request.GET.get("wilaya")
    print("Wilaya ID:------------>>>>>>>", wilaya_id)
    try:
        communes = Commune.objects.filter(wilaya_id=wilaya_id)
    except:
        return HttpResponse("<option>--------</option>")
    # return render(request, 'snippets/delivery/communes_options.html', {'communes': communes})
    response = render(request, "communes_options.html", {"communes": communes})
    response.headers["HX-Trigger"] = json.dumps(
        {
            "update_delivery_cost": None,
        }
    )
    return response
