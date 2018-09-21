from django.urls import path
from filestore import views

urlpatterns = [
    path('', views.FileList.as_view(), name='file-list'),
    path('add/', views.FileCreate.as_view(), name='file-create'),
    path('detail/<str:slug>', views.FileDetail.as_view(), name='file-detail'),
    path('delete/<str:slug>', views.FileDelete.as_view(), name='file-delete'),
    path('folders/', views.FolderList.as_view(), name='folder-list'),
    path('folders/add/', views.FolderCreate.as_view(), name='folder-create'),
    path('folders/detail/<str:pk>', views.FolderDetail.as_view(), name='folder-detail'),
    path('folders/delete/<str:pk>', views.FolderDelete.as_view(), name='folder-delete'),
    path('settings/clamav', views.clamav_settings, name='clamav-settings'),
]
