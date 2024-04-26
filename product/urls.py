from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.get_all_product,
    ),
    path(
        "get-all-product/",
        views.get_all_product,
    ),
    path(
        "add/",
        views.insert_product,
    ),
    path(
        "edit-product/<product_id>",
        views.edit_product,
    ),
    path(
        "delete-product/<product_id>",
        views.delete_product,
    ),
]
