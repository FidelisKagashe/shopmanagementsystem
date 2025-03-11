from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    DashboardView,
    # Product URLs
    ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    # Supplier URLs
    SupplierListView, SupplierDetailView, SupplierCreateView, SupplierUpdateView, SupplierDeleteView,
    # Customer URLs
    CustomerListView, CustomerDetailView, CustomerCreateView, CustomerUpdateView, CustomerDeleteView,
    # Purchase Order URLs
    PurchaseOrderListView, PurchaseOrderDetailView, PurchaseOrderCreateView, PurchaseOrderUpdateView, PurchaseOrderDeleteView,
    # Sale Order URLs
    SaleOrderListView, SaleOrderDetailView, SaleOrderCreateView, SaleOrderUpdateView, SaleOrderDeleteView,
    # Invoice URL
    InvoiceDetailView,
    # Sale Return URLs
    SaleReturnListView, SaleReturnCreateView,
    # Promotion URLs
    PromotionListView, PromotionCreateView, PromotionUpdateView, PromotionDeleteView,
    # Authentication & Miscellaneous
    CustomLoginView, Sold_products_view, lockout_view, logout_view,
    user_financial_transaction_view,
    transaction_detail_view,
    transaction_edit_view,
    transaction_delete_view,
    #Cash book
    user_financial_transaction_view,
)

urlpatterns = [
    # Authentication
    path('', CustomLoginView.as_view(), name='login'),
    path('lockout/', lockout_view, name='lockout'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Password Reset Request: Simple FBV
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('reset/<uidb64>/<token>/<request_token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/<uidb64>/<token>/', views.password_reset_form, name='password_reset_form'),
    
    # Resend Reset Code (optional)
    path('resend_reset_code/', views.resend_reset_code, name='resend_reset_code'),  # Endpoint to resend the reset code
    
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='Authentication/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='Authentication/password_change_done.html'), name='password_change_done'),

    # Product URLs
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    
    # Supplier URLs
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/update/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier_delete'),
    
    # Customer URLs
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    path('customers/create/', CustomerCreateView.as_view(), name='customer_create'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<int:pk>/update/', CustomerUpdateView.as_view(), name='customer_update'),
    path('customers/<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer_delete'),
    
    # Purchase Order URLs
    path('purchase_orders/', PurchaseOrderListView.as_view(), name='purchaseorder_list'),
    path('purchase_orders/create/', PurchaseOrderCreateView.as_view(), name='purchaseorder_create'),
    path('purchase_orders/<int:pk>/', PurchaseOrderDetailView.as_view(), name='purchaseorder_detail'),
    path('purchase_orders/<int:pk>/update/', PurchaseOrderUpdateView.as_view(), name='purchaseorder_update'),
    path('purchase_orders/<int:pk>/delete/', PurchaseOrderDeleteView.as_view(), name='purchaseorder_delete'),
    
    # Sale Order URLs
    path('sale_orders/', SaleOrderListView.as_view(), name='saleorder_list'),
    path('sale_orders/create/', SaleOrderCreateView.as_view(), name='saleorder_create'),
    path('sale_orders/<int:pk>/', SaleOrderDetailView.as_view(), name='saleorder_detail'),
    path('sale_orders/<int:pk>/update/', SaleOrderUpdateView.as_view(), name='saleorder_update'),
    path('sale_orders/<int:pk>/delete/', SaleOrderDeleteView.as_view(), name='saleorder_delete'),
    
    path('sold_products/', Sold_products_view, name='sold_products'),
    
    # Invoice URL
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    
    # Sale Return URLs
    path('sale_returns/', SaleReturnListView.as_view(), name='salereturn_list'),
    path('sale_returns/create/', SaleReturnCreateView.as_view(), name='salereturn_create'),
    
    # Promotion URLs
    path('promotions/', PromotionListView.as_view(), name='promotion_list'),
    path('promotions/create/', PromotionCreateView.as_view(), name='promotion_create'),
    path('promotions/<int:pk>/update/', PromotionUpdateView.as_view(), name='promotion_update'),
    path('promotions/<int:pk>/delete/', PromotionDeleteView.as_view(), name='promotion_delete'),

    #Cash book
    path('my-transactions/', user_financial_transaction_view, name='user_financial_transaction_view'),
    path('transaction/<int:pk>/view/', transaction_detail_view, name='transaction_detail_view'),
    path('transaction/<int:pk>/edit/', transaction_edit_view, name='transaction_edit_view'),
    path('transaction/<int:pk>/delete/', transaction_delete_view, name='transaction_delete_view'),
]
