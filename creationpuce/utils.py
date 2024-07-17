from django.db.models import Sum
from datetime import timedelta
from creationpuce.models import Production


def format_value(value):
    if value is None:
        return 0
    try:
        return f"{value:.2f}"
    except (TypeError, ValueError):
        return value

def get_dates_for_ligne():
    dates = Production.objects.values_list('date_production__date', flat=True).distinct()
    return [(date.strftime('%Y-%m-%d'), date.strftime('%d/%m/%Y')) for date in dates]


def get_weeks_for_ligne_or_secteur():
    weeks = Production.objects.dates('date_production', 'week').distinct()
    return [(week.strftime('%Y-%W'), f"Semaine {week.isocalendar()[1]}") for week in weeks]


def get_months_for_secteur():
    months = Production.objects.dates('date_production', 'month').distinct()
    return [(month.strftime('%Y-%m'), f"Mois {month.strftime('%B')}") for month in months]


# Fonctions pour préparer les données des graphiques
def prepare_desengagement_data(productions):
    return {
        'Essais / Validation': sum(
            p.arretdeproduction_set.filter(type_arret__nom__icontains='essai').aggregate(Sum('duree_en_heure'))[
                'duree_en_heure__sum'] or 0 for p in productions),
        'Maintenance Préventive Hebdo': sum(
            p.arretdeproduction_set.filter(type_arret__nom__icontains='maintenance').aggregate(Sum('duree_en_heure'))[
                'duree_en_heure__sum'] or 0 for p in productions),
        'Sous charge-Ligne fermée': sum(
            p.arretdeproduction_set.filter(type_arret__nom__icontains='sous charge').aggregate(Sum('duree_en_heure'))[
                'duree_en_heure__sum'] or 0 for p in productions),
    }


def prepare_arrets_induits_data(productions):
    return {
        'Traçabilité Panacim': sum(
            p.arretdeproduction_set.filter(type_arret__nom__icontains='traçabilité').aggregate(Sum('duree_en_heure'))[
                'duree_en_heure__sum'] or 0 for p in productions),
    }


def prepare_arrets_propres_data(productions):
    return {
        'Pb Qualité VAGUE': sum(
            p.arretdeproduction_set.filter(subtype_arret__nom__icontains='qualité').aggregate(Sum('duree_en_heure'))[
                'duree_en_heure__sum'] or 0 for p in productions),
        'Démarrage et Mise au Point': sum(
            p.arretdeproduction_set.filter(subtype_arret__nom__icontains='démarrage').aggregate(Sum('duree_en_heure'))[
                'duree_en_heure__sum'] or 0 for p in productions),
        'Changement de Série': sum(
            p.arretdeproduction_set.filter(subtype_arret__nom__icontains='changement').aggregate(Sum('duree_en_heure'))[
                'duree_en_heure__sum'] or 0 for p in productions),
        'Réglage/mise au point': sum(
            p.arretdeproduction_set.filter(subtype_arret__nom__icontains='réglage').aggregate(Sum('duree_en_heure'))[
                'duree_en_heure__sum'] or 0 for p in productions),
        'Pannes CMS': sum(
            p.arretdeproduction_set.filter(subtype_arret__nom__icontains='panne').aggregate(Sum('duree_en_heure'))[
                'duree_en_heure__sum'] or 0 for p in productions),
    }


def prepare_pannes_equipement_data(productions):
    return {moyen.nom: sum(
        p.arretdeproduction_set.filter(moyen=moyen).aggregate(Sum('duree_en_heure'))['duree_en_heure__sum'] or 0 for p
        in productions)
        for moyen in
        set(arret.moyen for p in productions for arret in p.arretdeproduction_set.all() if arret.moyen)}


def prepare_historique_trs_data(ligne, end_date):
    start_date = end_date - timedelta(weeks=11)  # Les 12 dernières semaines
    weeks = [start_date + timedelta(weeks=i) for i in range(12)]

    historique_trs = {}
    for week in weeks:
        productions = Production.objects.filter(
            ligne=ligne,
            date_production__week=week.isocalendar()[1],
            date_production__year=week.year
        )
        if productions.exists():
            trs_values = [p.calculate_trs() for p in productions]
            historique_trs[week.strftime('%Y-%W')] = sum(trs_values) / len(trs_values) if trs_values else 0
        else:
            historique_trs[week.strftime('%Y-%W')] = 0

    return historique_trs


def prepare_taux_effectif_data(productions):
    return {p.date_production.strftime('%Y-%m-%d'): p.nombre_operateur for p in productions}
