from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('upload', views.DataSheetView.as_view(), name="upload"),
    path('login', views.AuthView.as_view(), name="login"),
    path('logout', views.user_logout, name="logout"),
    path('view', views.view_data, name="view"),
    path('admin/users', views.manage_users, name="manage_user"),
    path('admin', views.super_user, name="super_user"),
    path('admin/users/assignmarket', views.assign_market, name="assign_market"),
    path('admin/users/changepassword', views.change_user_password, name="change_password"),
    path('admin/users/delete', views.delete_user, name="delete_user"),
    path('admin/users/add', views.add_user, name="add_user"),
    path('admin/changepassword', views.change_my_password, name="change_my_password")

]