from django.urls import path, include
from . import views

urlpatterns = [
    path(
        "",
        views.index,
    ),
    path("accounts/login/", views.login, name="login"),
    path(
        "product-list/",
        views.get_all_product,
    ),
    path("add/", views.insert_product, name="insert_product"),
    path("edit-product/<product_id>", views.edit_product, name="edit_product"),
    path("delete-product/<product_id>", views.delete_product, name="delete_product"),
]
