from django.conf.urls.static import static
from django.urls import path
from myProject import settings
from django.contrib.auth import views as auth_views
from . import views
from .views import add_to_cart, buy_now, buy_paintings, checkout, complete_payment, order_success, payment_page, remove_from_cart, update_profile_picture, toggle_follow, follow_list, follow_user, follow_list_profile, user_profile, view_cart

urlpatterns = [
    path('logout/', views.user_logout, name='logout'),
    path('', views.user_login, name='login'),  # Login as the default page
    #path('register/', views.register, name='register'),
    path('signup/', views.register, name='signup'),
    path('home/', views.home, name="home"),
    path('auction/upcoming/', views.upcoming_auction, name='upcoming_auction'),
    path('auction/live/', views.live_auction, name='live_auction'),
    path('auction/auction_results/', views.auction_results, name='auction_results'),
    path('auction/place-bid/<int:painting_id>/', views.place_bid, name='place_bid'),
    path('auction/upcoming/<int:painting_id>/', views.upcoming_auction, name='upcoming_auction'),
    #path('auction/upcoming/', views.upcoming_auction, name='upcoming_auction'),
    path('add-to-cart/<int:painting_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('order-success/', order_success, name='order_success'), 
    path('complete-payment/<int:order_id>/', complete_payment, name='complete_payment'),
    path('payment/<int:order_id>/', payment_page, name='payment_page'),
    path('buy-now/<int:painting_id>/', buy_now, name='buy_now'),
    path('buy/', buy_paintings, name='buy'),
    path('sell/', views.sell, name='sell'),
    path('upload_painting/', views.upload_painting, name='upload_painting'),
    path('search/', views.search_paintings, name='search_paintings'),
    path('search-users/', views.search_users, name='search_users'),
    path('user/<str:username>/', views.user_paintings, name='user_paintings'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('guest_upload_painting/', views.guest_upload_painting, name='guest_upload_painting'),
    path('continue_without_login/', views.set_guest_mode, name='continue_without_login'),
    path('painting/<int:painting_id>/', views.painting_detail, name='painting_detail'),
    path('profile-settings/', views.user_profile, name='user_profile_settings'),
    path('profile/<str:username>/', views.profile_settings, name='profile-settings'),
    path("profile-settings/", user_profile, name="user_profile"),
    path("update-profile-picture/", update_profile_picture, name="update_profile_picture"),
    path('update_settings/', views.update_user_settings, name='update_user_settings'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('payment_simulation/<int:painting_id>/', views.payment_simulation, name='payment_simulation'),
    path("update-profile-picture/", update_profile_picture, name="update_profile_picture"),
    path("toggle-follow/", toggle_follow, name="toggle_follow"),
    path("follow/<str:username>/", follow_user, name="follow_user"),  # Make sure this comes FIRST
    path("<str:username>/<str:follow_type>/", follow_list, name="follow_list"),
    path('profile/<str:username>/', views.profile_settings, name='profile_settings'),
    path("<str:username>/<str:follow_type>/", follow_list_profile, name="follow_list_profile"),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:  # Only serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

