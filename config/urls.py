"""acm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from config import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls

# sitemaps = {
#     'terms': TermsSitemap,
#     'faq': FAQSitemap,
#     'static': StaticSitemap
# }
urlpatterns = [
    # path('markdownx/', include('markdownx.urls')),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("apps.core.urls")),
    path("", include("apps.transactions.urls")),
    path("", include("apps.crm.urls")),
    path("", include("apps.users.urls")),
    path("", include("apps.wilayas.urls")),
    path("", include("apps.leads.urls")),
    path("", include("apps.billing.urls")),
    path("", include("apps.business.urls")),
    path("", include("apps.notification.urls")),
    path("", include("apps.appointment.urls")),
    path("", include("apps.subscription.urls")),
    path("", include("apps.tags.urls")),
    
    path('tinymce/', include('tinymce.urls')),

    # path('sitemap.xml', sitemap, {'sitemaps': sitemaps},name='django.contrib.sitemaps.views.sitemap'),
] + debug_toolbar_urls()


if settings.DEBUG:
    # import debug_toolbar
    urlpatterns += [
        path("admin/", admin.site.urls),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += path('__debug__/', include("debug_toolbar.urls")),
