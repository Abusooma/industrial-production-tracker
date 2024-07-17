from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('secteurs/', views.secteur, name='secteur'),
    path('features/', views.features, name='features'),
    path('start/production-create-step1', views.create_produit_step1, name='step1'),
    path('admin-menu/', views.adminMenu, name='admin-menu'),
    path('<int:pk>/', views.create_produit_step1, name='update-step1'),
    path('create-produit-step2/', views.create_produit_step2, name='step2'),
    path('create-produit-step3/', views.create_produit_step3, name='step3'),
    path('load-lignes/', views.load_lignes, name='load_lignes'),
    path('load-subtypes/', views.load_subtypes, name='load_subtypes'),
    path('load-detailsubtypes/', views.load_detailsubtypes, name='load_detailsubtypes'),
    path('load_horaires/', views.load_horaires, name='load_horaires'),
    path('load_face_du_produit/', views.load_faceproduit, name='load-face-produit'),
    path('load_produit/', views.load_products, name='load_products'),
    path('load_produit_by_family/', views.load_product_by_family, name='load_products_by_family'),
    path('load_moyen/', views.load_moyen, name='load-moyen'),
    path('load-tcm/', views.load_tcm, name='load_tcm'),
    path('manage-display-btn/', views.manageBtn, name='manage-btn-next'),
    path('manage-display-btnfinish/', views.manageBtnFinish, name='manage-btn-finish'),

    path('saisir-temps-de-cycle/', views.saisir_temps_de_cycle, name='saisir_temps_de_cycle'),
    path('load-more-temps-de-cycles/', views.load_more_temps_de_cycles, name='load_more_temps_de_cycles'),

    path('objectif_changeover/', views.objectif_changeover_view, name='objectif_changeover_view'),
    path('get-obi-value/', views.get_obi_value, name='get_obi_value'),

    path('ajouter_produit/', views.ajouter_produit, name='ajouter_produit'),
    path('ajouter_ligne/', views.ajouter_ligne, name='ajouter_ligne'),
    path('ajouter_secteur/', views.ajouter_secteur, name='ajouter_secteur'),
    path('ajouter_client/', views.ajouter_client, name='ajouter_client'),
    path('ajouter_equipe/', views.ajouter_equipe, name='ajouter_equipe'),
    path('ajouter_arret/', views.ajouter_arret, name='ajouter_arret'),
    path('ajouter_subtype_arret/', views.ajouter_subtype_arret, name='ajouter_subtype_arret'),
    path('ajouter_detail_subtype_arret/', views.ajouter_detail_subtype_arret, name='ajouter_detail_subtype_arret'),
    path('ajouter_moyen/', views.ajouter_moyen, name='ajouter_moyen'),

    path('reports/', views.index_report, name='index_report'),
    path('generate_report_form/<str:report_type>/', views.generate_report_form, name='generate_report_form'),
    path('generate_daily_line_pdf/', views.generate_daily_line_pdf, name='generate_daily_line_pdf'),
    path('report/generate_weekly_line_pdf/', views.generate_weekly_line_report, name='generate_weekly_line_pdf'),
]
