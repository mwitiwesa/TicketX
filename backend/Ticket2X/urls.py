from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views  

urlpatterns = [
    path('admin/', admin.site.urls),

    # Accounts app (custom login, register, etc.)
    path('accounts/', include('apps.accounts.urls')),

    # Built-in auth URLs (for password reset, etc.) - but avoid conflict with login
    path('auth/', include('django.contrib.auth.urls')),

    path('events/', include('apps.events.urls')),
    path('bookings/', include('apps.bookings.urls')),
    path('calendar/', include('apps.calendar_view.urls')), 
    path('', include('apps.core.urls')),
path('search/', core_views.search, name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)