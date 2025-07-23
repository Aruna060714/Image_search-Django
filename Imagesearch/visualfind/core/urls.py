from django.urls import path
from .views import index_view, upload_view, all_products_view
urlpatterns = [
    path('', index_view, name='index'),
    path('upload/', upload_view, name='upload'),
    path('all-products/', all_products_view, name='all_products'),
]