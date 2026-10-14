from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("products/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]