from django.urls import path
from . import views

urlpatterns = [
    path('users/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('',views.getRoutes,name='routes'),
    path('users/profile/',views.getUserProfile, name='user profile'),
    path('users/register/',views.registerUser, name='user register'),
    path('users/profile/update/',views.updateUserProfile, name="profile-update"),
    path('users/delete/',views.deleteUser, name='delete-user'),

    path('inventory/',views.getAllInventory, name="All-Inventory"),
    path('inventory/create/',views.createInventoryItem, name="Create-Inventory"),
    path('inventory/<str:filter_key>/',views.getInventory, name="Get-Certain-Inventory"),
    path('inventory/<str:filter_key>/update/',views.updateInventoryItem, name="Update-Inventory"),
    path('inventory/<str:filter_key>/delete/',views.deleteInventoryItem,name="Delete_Inventory"),

    path('createpaymentmethod/',views.createPaymentMethod,name="paymentmethod"),
    path('subscribe/',views.save_stripe_info,name="subscription"),
    path('cancelsubscription/',views.CancelSubscription.as_view(),name="Cancel-Subscription")
]