from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"livros", views.LivroViewSet)
router.register(r"autores", views.AutorViewSet)
router.register(r"categorias", views.CategoriaViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('', views.ApiRoot.as_view(), name=views.ApiRoot.name),
]
