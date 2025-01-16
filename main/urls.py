from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('product/<int:product_id>/', views.product_details, name='product_details'),
    path('seller/register/', views.create_seller, name='seller_registration'),
    path('customer/register/', views.customer_signup, name='customer_signup'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/', views.cart_detail, name='cart_detail'),  # View cart details
    path('cart/update/<int:item_id>/', views.update_cart, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout_page, name='checkout'),
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-seller/', views.create_seller, name='create_seller'),
    path('create-category/', views.create_category, name='create_category'),
    path('create-product/', views.create_product, name='create_product'),
    path('delete_seller/<int:seller_id>/', views.delete_seller, name='delete_seller'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('edit_seller/<int:seller_id>/', views.edit_seller, name='edit_seller'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
]
