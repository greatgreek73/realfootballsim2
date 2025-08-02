from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Сохраняем /api/, если он есть. Если его нет — этот include можно убрать.
try:
    urlpatterns += [path('api/', include(('api.urls', 'api'), namespace='api'))]
except Exception:
    pass

# Catch-all: отдаём front/index.html для всех путей, кроме /static/
urlpatterns += [
    re_path(r"^(?!static/).*", TemplateView.as_view(template_name="index.html")),
]
