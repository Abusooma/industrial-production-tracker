from datetime import datetime, timedelta
from dateutil import parser
from babel.dates import format_date
from django.db import models


# TABLE SECTEUR
class Secteur(models.Model):
    nom_secteur = models.CharField(max_length=200)

    def __str__(self):
        return self.nom_secteur if self.nom_secteur else "N/A"


# TABLE LIGNE
class Ligne(models.Model):
    secteur = models.ForeignKey(Secteur, on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)

    def __str__(self):
        return self.nom


# TABLE ARRET
class Arret(models.Model):
    nom = models.CharField(max_length=200)
    commentaire = models.TextField(max_length=200, blank=True, null=True)
    heure_et_minute = models.TimeField(blank=True, null=True)

    def __str__(self):
        return self.nom


# TABLE SUBTYPE D'UN ARRET
class SubTypeArret(models.Model):
    arret = models.ForeignKey(Arret, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.description


# DETAILS D'UN SUBTYPE DE L'ARRET
class DetailSubTypeArret(models.Model):
    arret = models.ForeignKey(Arret, on_delete=models.CASCADE)
    sub_type_arret = models.ForeignKey(SubTypeArret, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.description


# TABLE DE LA MACHINE D'UNE LIGNE
class Moyen(models.Model):
    ligne = models.ForeignKey(Ligne, on_delete=models.CASCADE, null=True, blank=True)
    subtype_arret = models.ForeignKey(SubTypeArret, on_delete=models.CASCADE, null=True, blank=True)
    nom = models.CharField(max_length=200)
    heure_debut = models.TimeField(blank=True, null=True)  # Temps de début d'opération
    heure_fin = models.TimeField(blank=True, null=True)  # Temps de fin d'opération

    def __str__(self):
        return self.nom if self.nom else "N/A"


# TABLE L'EQUIPE
class Equipe(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


# TABLE PLAGE DE TRAVAIL DE L'EQUIPE
class PlageDeTravail(models.Model):
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE)
    debut = models.TimeField()
    fin = models.TimeField()

    def __str__(self):
        return f"{self.equipe.nom}: {self.debut.strftime('%H:%M')} - {self.fin.strftime('%H:%M')}"


# TABLE DE LA FACE DU PRODUIT
class FaceProduit(models.Model):
    secteur = models.ForeignKey(Secteur, on_delete=models.CASCADE, null=True)
    nom = models.CharField(max_length=25)

    def __str__(self):
        return self.nom if self.nom else "N/A"


# TABLE Famille
class Famille(models.Model):
    nom = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.nom if self.nom else "N/A"


class Client(models.Model):
    nom = models.CharField(max_length=155)

    def __str__(self):
        return self.nom if self.nom else "N/A"


# TABLE PRODUIT
class Produit(models.Model):
    famille = models.ForeignKey(Famille, on_delete=models.CASCADE, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    code_ac = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.code_ac if self.code_ac else "N/A"


class Production(models.Model):
    ligne = models.ForeignKey(Ligne, on_delete=models.CASCADE, null=True)
    secteur = models.ForeignKey(Secteur, on_delete=models.CASCADE, null=True)
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE, null=True)
    date_production = models.DateTimeField()
    nombre_operateur = models.IntegerField(default=2)

    def __str__(self):
        return f"{self.secteur.nom_secteur} - {self.ligne.nom} - {self.date_production.strftime('%Y-%m-%d')}"

    def get_week(self):
        if isinstance(self.date_production, str):
            self.date_production = parser.parse(self.date_production)
        return self.date_production.isocalendar()[1]

    def get_month(self):
        if isinstance(self.date_production, str):
            self.date_production = parser.parse(self.date_production)
        return format_date(self.date_production, format='MMMM', locale='fr')

    def sum_temps_ouverture(self):
        return sum(step.temps_ouverture() or 0 for step in self.productionsteptwo_set.all())

    def sum_non_qualite(self):
        return sum(step.non_quality() or 0 for step in self.productionsteptwo_set.all())

    def sum_desengagement(self):
        return sum(
            (arret.duree_en_heure or 0) + (arret.duree_en_minute or 0) / 60
            for arret in self.arretdeproduction_set.filter(type_arret__nom__icontains="engagement")
        )

    def sum_arret_propre(self):
        return sum(
            (arret.duree_en_heure or 0) + (arret.duree_en_minute or 0) / 60
            for arret in self.arretdeproduction_set.filter(type_arret__nom__icontains="propre")
        )

    def sum_arret_induit(self):
        return sum(
            (arret.duree_en_heure or 0) + (arret.duree_en_minute or 0) / 60
            for arret in self.arretdeproduction_set.filter(type_arret__nom__icontains="induit")
        )

    def sum_all_arrets(self):
        return sum(
            (arret.duree_en_heure or 0) + (arret.duree_en_minute or 0) / 60
            for arret in self.arretdeproduction_set.all()
        )

    def calculate_tr(self):
        return max(0, self.sum_temps_ouverture() - self.sum_desengagement())

    def calculate_tf(self, tr):
        return max(0, tr - (self.sum_arret_propre() + self.sum_arret_induit()))

    def calculate_ecart_de_cadence(self, tf):
        return max(0, self.sum_temps_ouverture() - (tf - self.sum_all_arrets()))

    def calculate_tn(self, tf, ecart_de_cadence):
        return max(0, tf - ecart_de_cadence)

    def calculate_tu(self):
        tr = self.calculate_tr()
        tf = self.calculate_tf(tr)
        ecart_de_cadence = self.calculate_ecart_de_cadence(tf)
        tn = self.calculate_tn(tf, ecart_de_cadence)
        return max(0, tn - self.sum_non_qualite())

    def calculate_trs(self):
        tr = self.calculate_tr()
        tu = self.calculate_tu()
        if tr == 0:
            return 0
        return min(100, (tu / tr) * 100)  # Assurez-vous que TRS ne dépasse pas 100%


class Intervenant(models.Model):
    poste = models.CharField(max_length=155)

    def __str__(self):
        return self.poste


class Changement(models.Model):
    description = models.CharField(max_length=255)
    detail_type_arret = models.ForeignKey(DetailSubTypeArret, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.description}"


class ProductionStepTwo(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    face_du_produit = models.ForeignKey(FaceProduit, on_delete=models.CASCADE, null=True)
    heure_debut = models.TimeField(null=True)
    heure_fin = models.TimeField(null=True)
    quantity_fs = models.IntegerField(null=True, blank=True)
    quantity_fc = models.IntegerField(null=True, blank=True)
    defaults = models.IntegerField(null=True, default=0)

    def __str__(self):
        return f"{self.production.id} - {self.produit} - {self.client}"

    def calculate_fpy(self):
        total_quantity = (self.quantity_fc or 0) + (self.quantity_fs or 0)
        defaults = self.defaults or 0
        if total_quantity == 0:
            return 0
        good_products = total_quantity - defaults
        return (good_products / total_quantity) * 100

    def temps_ouverture(self):
        if self.heure_debut and self.heure_fin:
            debut = datetime.combine(datetime.today(), self.heure_debut)
            fin = datetime.combine(datetime.today(), self.heure_fin)
            if fin < debut:
                fin += timedelta(days=1)
            opening_time = fin - debut
            return opening_time.total_seconds() / 3600  # Return in hours
        return 0

    def calculate_tuf(self):
        quantity_fs = self.quantity_fs or 0
        quantity_fc = self.quantity_fc or 0
        defaults = self.defaults or 0
        tcm = 0
        temps_de_cycle = TempsDeCycle.objects.filter(secteur=self.production.secteur, produit=self.produit).first()
        if temps_de_cycle:
            tcm = temps_de_cycle.tcm
        total_quantity = quantity_fs + quantity_fc + defaults
        if total_quantity == 0:
            return 0

        tuf = (tcm * total_quantity) / 3600

        return float(tuf)

    def non_quality(self):
        defaults = self.defaults or 0
        tcm = 0
        temps_de_cycle = TempsDeCycle.objects.filter(secteur=self.production.secteur, produit=self.produit).last()
        if temps_de_cycle:
            tcm = temps_de_cycle.tcm
        return float(defaults * tcm)

    def calcul_initial_trs(self):
        tuf = self.calculate_tuf()
        temps_ouverture = self.temps_ouverture()
        if temps_ouverture > 0:
            return (tuf / temps_ouverture) * 100
        return 0


class ArretDeProduction(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE, null=True)
    type_arret = models.ForeignKey(Arret, on_delete=models.CASCADE, null=True)
    subtype_arret = models.ForeignKey(SubTypeArret, on_delete=models.CASCADE, blank=True, null=True)
    detail_sub_type_arret = models.ForeignKey(DetailSubTypeArret, on_delete=models.CASCADE, null=True, blank=True)
    moyen = models.ForeignKey(Moyen, on_delete=models.CASCADE, blank=True, null=True)
    duree_en_heure = models.IntegerField(null=True, blank=True)
    duree_en_minute = models.IntegerField(null=True, blank=True)
    commentaire = models.TextField(blank=True, null=True)
    intervenant = models.ForeignKey(Intervenant, on_delete=models.CASCADE, null=True, blank=True)
    changement = models.ForeignKey(Changement, on_delete=models.CASCADE, null=True, blank=True)
    action = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.type_arret} - {self.subtype_arret}"


class TempsDeCycle(models.Model):
    ligne = models.ForeignKey(Ligne, on_delete=models.CASCADE, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, null=True)
    face = models.ForeignKey(FaceProduit, on_delete=models.CASCADE, null=True)
    moyen = models.ForeignKey(Moyen, on_delete=models.CASCADE, null=True)
    tcm = models.DecimalField(max_digits=10, decimal_places=2, help_text="Temps de cycle moyen en Heure", blank=True,
                              null=True)
    commentaire = models.CharField(max_length=155, blank=True, null=True)

    def __str__(self):
        produit_str = str(self.produit) if self.produit else "N/A"
        face_str = str(self.face) if self.face else "N/A"
        tcm_str = str(self.tcm) if self.tcm else "N/A"

        return f"{produit_str} - {face_str} - {tcm_str}"


class ObjectifChangeOver(models.Model):
    secteur = models.ForeignKey(Secteur, on_delete=models.CASCADE)
    ligne = models.ForeignKey(Ligne, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    famille = models.ForeignKey(Famille, on_delete=models.CASCADE, null=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Objective ChangeOver : ID: {self.pk} - Produit : {self.produit.code_ac} - Famille : {self.famille.nom}"


class TypeDeChangementDeObjectif(models.Model):
    objectif = models.ForeignKey(ObjectifChangeOver, on_delete=models.CASCADE, related_name='values')
    changement = models.ForeignKey(Changement, on_delete=models.CASCADE)
    valeur = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.changement.description} - {self.objectif.id}"
