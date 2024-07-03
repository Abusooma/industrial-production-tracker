from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_produit_step1, name='step1'),
    path('admin-menu/', views.adminMenu, name='admin-menu'),
    path('<int:pk>/', views.create_produit_step1, name='update-step1'),
    path('create-produit-step2/', views.create_produit_step2, name='step2'),
    path('create-produit-step3/', views.create_produit_step3, name='step3'),
    path('load-lignes/', views.load_lignes, name='load_lignes'),
    path('load-subtypes/', views.load_subtypes, name='load_subtypes'),
    path('load-detailsubtypes/', views.load_detailsubtypes, name='load_detailsubtypes'),
    path('load_horaires/', views.load_horaires, name='load_horaires'),
    path('load_face_du_produit/', views.load_faceproduit, name='load-face-produit'),
    path('load_moyen/', views.load_moyen, name='load-moyen'),
    path('load-tcm/', views.load_tcm, name='load_tcm'),
    path('manage-display-btn/', views.manageBtn, name='manage-btn-next'),
    path('manage-display-btnfinish/', views.manageBtnFinish, name='manage-btn-finish'),

    path('saisir-temps-de-cycle/', views.saisir_temps_de_cycle, name='saisir_temps_de_cycle'),
    path('load-more-temps-de-cycles/', views.load_more_temps_de_cycles, name='load_more_temps_de_cycles'),
]
