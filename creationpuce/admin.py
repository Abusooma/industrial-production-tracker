from django.contrib import admin
from .models import Secteur, Ligne, Arret, SubTypeArret, DetailSubTypeArret, Moyen, Equipe, PlageDeTravail, Produit, \
    Production, Client, ArretDeProduction, FaceProduit, TempsDeCycle, Intervenant, Changement, ProductionStepTwo, \
    TypeDeChangementDeObjectif, ObjectifChangeOver,Famille

admin.site.register(Secteur)
admin.site.register(Ligne)
admin.site.register(Arret)
admin.site.register(SubTypeArret)
admin.site.register(DetailSubTypeArret)
admin.site.register(Moyen)
admin.site.register(Equipe)
admin.site.register(PlageDeTravail)
admin.site.register(Produit)
admin.site.register(Production)
admin.site.register(Client)
admin.site.register(ArretDeProduction)
admin.site.register(FaceProduit)
admin.site.register(TempsDeCycle)
admin.site.register(Intervenant)
admin.site.register(Changement)
admin.site.register(ProductionStepTwo)
admin.site.register(TypeDeChangementDeObjectif)
admin.site.register(ObjectifChangeOver)
admin.site.register(Famille)