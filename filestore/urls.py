from django.urls import path
from filestore import views

urlpatterns = [
    path('', views.index, name='index'),
    path('files/', views.FileList.as_view(), name='file-list'),
    path('add/', views.FileCreate.as_view(), name='file-create'),
    path('detail/<str:slug>', views.FileDetail.as_view(), name='file-detail'),
    path('delete/<str:slug>', views.FileDelete.as_view(), name='file-delete'),
    path('folders/', views.FolderList.as_view(), name='folder-list'),
    path('folders/add/', views.FolderCreate.as_view(), name='folder-create'),
    path('folders/detail/<str:pk>', views.FolderDetail.as_view(), name='folder-detail'),
    path('folders/delete/<str:pk>', views.FolderDelete.as_view(), name='folder-delete'),
    path('settings/<str:slug>', views.SettingsUpdate.as_view(), name='settings'),
    path('update_clamav_db', views.update_clamav_db, name='update-clamav-db'),
]
