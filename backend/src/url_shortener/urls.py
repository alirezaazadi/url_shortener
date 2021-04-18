from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('app_users.urls')),
    path('api/shrt/', include('app_shortener.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend([
        path('__debug__/', include(debug_toolbar.urls))
    ])
