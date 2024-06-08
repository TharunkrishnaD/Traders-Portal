from django.urls import path
from .import views

urlpatterns= [
   path('',views.signIn,name="signIn"),
   path('signup/',views.signup,name="signup"),
   path('list/',views.list,name="list"),
   path('firebase_login_save/', views.firebase_login_save),
   path('postsignIn/', views.postsignIn,name="postsignIn"),
   path('postsignUp/', views.postsignUp,name="postsignUp"),
    path('add-to-watchlist/<int:company_id>/', views.add_to_watchlist, name='add_to_watchlist'),
     path('watchlist/', views.watchlist, name='watchlist'),
    path('remove/<int:company_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
#    path('googleSignIn/', views.googleSignIn, name='googleSignIn'),
#    path('google/login/', views.google_login, name='google_login'),
#     path('google/callback/', views.google_callback, name='google_callback'),
]