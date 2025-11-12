from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('authentication.urls')),
    path('api/v1/', include('technologies.urls')),
    path('api/v1/', include('profiles.urls')),
    path('api/v1/', include('articles.urls')),
    path('api/v1/', include('questions.urls')),
    path('api/v1/', include('answers.urls')),
    path('api/v1/', include('credentials.urls')),
    path('documentation/', include('documentation.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
