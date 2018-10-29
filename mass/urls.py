from django.conf import settings
from django.urls import include, path


urlpatterns = [
    path('', include('filestore.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),

    ]
    SHOW_TOOLBAR_CALLBACK = True
