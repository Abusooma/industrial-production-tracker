from datetime import timedelta, datetime

import matplotlib.pyplot as plt
import matplotlib
import pytz

from django.conf import settings

matplotlib.use('Agg')

import os
import io
import base64

from django.contrib import messages
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, ExpressionWrapper, FloatField
from django.db.models.functions import Coalesce
from django.template.loader import render_to_string, get_template
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404

# import pour le PDF
from xhtml2pdf import pisa
from io import BytesIO

from .forms import (ProduitCreationForm, ArretForm, ProductionDetailsForm, TempsDeCycleForm, ObjectifChangeOverForm,
                    TypeDeChangementDeObjectifForm, ProduitForm, LigneForm, SecteurForm, ArretSimpleForm,
                    SubTypeArretForm, DetailSubTypeArretForm, MoyenForm, EquipeForm, ClientForm, ReportForm)
from .models import (Ligne, SubTypeArret, DetailSubTypeArret, Production, Produit, Equipe, FaceProduit, TempsDeCycle,
                     ProductionStepTwo, ArretDeProduction, Moyen, TypeDeChangementDeObjectif, ObjectifChangeOver,
                     Changement)

from .utils import (format_value, get_dates_for_ligne, get_months_for_secteur, get_weeks_for_ligne_or_secteur,
                    get_pannes_equipement_data, get_arrets_data, get_product_details)


def accueil(request):
    return render(request, 'create/page_acceuil.html')


def features(request):
    return render(request, 'create/features.html')


@login_required
def secteur(request):
    return render(request, 'create/secteurs.html')


@login_required
def create_produit_step1(request, pk=None):
    if pk is not None:
        production = get_object_or_404(Production, pk=pk)
    else:
        production = None

    if request.method == 'POST':
        if production:
            form = ProduitCreationForm(request.POST, instance=production)
        else:
            form = ProduitCreationForm(request.POST)
        if form.is_valid():
            production_instance = form.save(commit=False)
            production_instance.save()
            request.session['production_instance_id'] = production_instance.id

            return redirect('step2')
    else:
        form = ProduitCreationForm(instance=production)

    return render(request, 'create/index.html', context={'form': form})


@login_required
def create_produit_step2(request):
    production_instance_id = request.session.get('production_instance_id')

    if not production_instance_id:
        return redirect('step1')

    try:
        production_instance = Production.objects.get(id=production_instance_id)
    except Production.DoesNotExist:
        return redirect('step1')

    equipe_id = production_instance.equipe.id
    secteur_id = production_instance.secteur.id
    ligne_id = production_instance.ligne.id

    if request.method == 'POST':
        form = ProductionDetailsForm(request.POST, secteur_id=secteur_id)
        if form.is_valid():
            production_step_two = form.save(commit=False)
            production_step_two.production = production_instance
            production_step_two.save()
            message = 'Données ajoutées avec success ...!'
            message_type = 'success'

        else:
            message = 'Formulaire invalid'
            message_type = 'danger'

        return JsonResponse({'success': message, 'message_type': message_type})

    else:
        form = ProductionDetailsForm(secteur_id=secteur_id)
        message = None
        message_type = None

    context = {
        'form': form,
        'production_instance': production_instance,
        'equipe_id': equipe_id,
        'secteur_id': secteur_id,
        'ligne_id': ligne_id,
        'message': message,
        'message_type': message_type
    }

    return render(request, 'create/create_produit_step2.html', context=context)


@login_required
def create_produit_step3(request):
    production_instance_id = request.session.get('production_instance_id')

    if not production_instance_id:
        return redirect('step1')

    if request.GET.get('finish'):
        del request.session['production_instance_id']
        return redirect('step1')
    try:
        production_instance = Production.objects.get(id=production_instance_id)
    except Production.DoesNotExist:
        return redirect('step1')

    ligne_id = production_instance.ligne.id
    production_step_two = ProductionStepTwo.objects.filter(production=production_instance).last()
    produit = production_step_two.produit
    client = production_step_two.client
    face_du_produit_id = production_step_two.face_du_produit.id

    if request.method == 'POST':
        form = ArretForm(request.POST, ligne_id=ligne_id)
        if form.is_valid():
            arret = form.save(commit=False)
            arret.production = production_instance
            arret.save()

            message = 'Arrêt ajouté avec succès'
            message_type = 'success'
        else:
            message = 'Formulaire invalide'
            message_type = 'danger'

        return JsonResponse({'success': message, 'message_type': message_type})

    else:
        form = ArretForm(ligne_id=ligne_id)
        message = None
        message_type = None

    context = {
        'form': form,
        'production_instance': production_instance,
        'message': message,
        'message_type': message_type,
        'produit': produit,
        'client': client,
        'ligne_id': ligne_id,
        'face_du_produit_id': face_du_produit_id
    }

    return render(request, 'create/create_produit_step3.html', context=context)


def adminMenu(request):
    return render(request, 'create/admin_menu.html')


def objectif_changeover_view(request):
    TypeDeChangementDeObjectifFormSet = inlineformset_factory(
        ObjectifChangeOver,
        TypeDeChangementDeObjectif,
        form=TypeDeChangementDeObjectifForm,
        extra=4,
        can_delete=True
    )

    if request.method == "POST":
        objectif_form = ObjectifChangeOverForm(request.POST)
        formset = TypeDeChangementDeObjectifFormSet(request.POST, instance=None)

        if objectif_form.is_valid() and formset.is_valid():
            objectif = objectif_form.save()
            formset.instance = objectif
            formset.save()
            messages.success(request, 'Objective Change sauvegardé avec success ..!')
            return redirect('objectif_changeover_view')
        else:
            messages.error(request, 'Erreur d\'enregistrement ....!')
    else:
        initial_data = [
            {'changement': Changement.objects.filter(description__icontains='Commun').first()},
            {'changement': Changement.objects.filter(description__icontains='spécifique').first()},
            {'changement': Changement.objects.filter(description__icontains='Version').first()},
            {'changement': Changement.objects.filter(description__icontains='face').first()}
        ]
        objectif_form = ObjectifChangeOverForm()
        formset = TypeDeChangementDeObjectifFormSet(queryset=TypeDeChangementDeObjectif.objects.none(), instance=None,
                                                    initial=initial_data)

    return render(request, 'create/objectif_changeover.html', {
        'objectif_form': objectif_form,
        'formset': formset,
    })


def load_products(request):
    client_id = request.GET.get('client_id')
    print(client_id)
    products = Produit.objects.filter(client_id=client_id).values('id', 'code_ac')
    return JsonResponse(list(products), safe=False)


def load_lignes(request):
    secteur_id = request.GET.get('secteur')
    lignes = Ligne.objects.filter(secteur_id=secteur_id).order_by('nom')
    return JsonResponse(list(lignes.values('id', 'nom')), safe=False)


def load_subtypes(request):
    arret_id = request.GET.get('arret_id')
    subtypes = SubTypeArret.objects.filter(arret_id=arret_id).values('id', 'description')
    return JsonResponse(list(subtypes), safe=False)


def load_detailsubtypes(request):
    subtype_arret_id = request.GET.get('subtype_arret_id')
    details = DetailSubTypeArret.objects.filter(sub_type_arret=subtype_arret_id).values('id', 'description')
    return JsonResponse(list(details), safe=False)


def load_faceproduit(request):
    secteur_id = request.GET.get('secteur')
    faceproduit = FaceProduit.objects.filter(secteur_id=secteur_id).values('id', 'nom')
    return JsonResponse(list(faceproduit), safe=False)


def load_moyen(request):
    ligne_id = request.GET.get('ligne_id')
    moyen = Moyen.objects.filter(ligne_id=ligne_id).values('id', 'nom')
    return JsonResponse(list(moyen), safe=False)


def load_horaires(request):
    equipe_id = request.GET.get('equipe')
    equipe = Equipe.objects.get(id=equipe_id)

    horaires = {
        'MATIN': {
            'debut': ['06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
                      '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:30', '16:15'],
            'fin': ['06:48', '07:18', '07:48', '08:18', '08:48', '09:18', '09:48', '10:18', '10:48', '11:18', '11:48',
                    '12:18', '12:48', '13:18', '13:48', '14:18', '14:48', '15:18', '15:48', '16:18']
        },
        'SOIR': {
            'debut': ['14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
                      '20:00', '20:30', '21:00', '21:30', '22:00'],
            'fin': ['14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
                    '20:00', '20:30', '21:00', '21:30', '22:30']
        },
        'NUIT': {
            'debut': ['22:00', '22:30', '23:00', '23:30', '00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00',
                      '03:30', '04:00', '04:30', '05:00', '05:30', '06:00'],
            'fin': ['22:30', '23:00', '23:30', '00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30',
                    '04:00', '04:30', '05:00', '05:30', '06:30']
        }
    }

    return JsonResponse({'horaires': horaires.get(equipe.nom, {'debut': [], 'fin': []})})


def load_product_by_family(request):
    famille_id = request.GET.get('famille_id')
    produit = Produit.objects.filter(famille_id=famille_id).values('id', 'code_ac')
    return JsonResponse(list(produit), safe=False)


def load_tcm(request):
    ligne_id = request.GET.get('ligne_id')
    produit_id = request.GET.get('produit_id')
    client_id = request.GET.get('client_id')

    try:
        tcm = TempsDeCycle.objects.filter(ligne_id=ligne_id, client_id=client_id, produit_id=produit_id).first().tcm
        return JsonResponse({'tcm': tcm})
    except TempsDeCycle.DoesNotExist:
        return JsonResponse({'tcm': None}, status=404)


def manageBtn(request):
    production_id = request.GET.get('production_id')
    production = Production.objects.get(id=production_id)
    production_step_two = ProductionStepTwo.objects.filter(production=production)
    if production_step_two:
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def manageBtnFinish(request):
    production_id = request.GET.get('production_id')
    production = Production.objects.get(id=production_id)
    arret = ArretDeProduction.objects.filter(production=production).first()

    if arret:
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def get_obi_value(request):
    ligne = request.GET.get('ligne')
    client = request.GET.get('client')
    changement = request.GET.get('changement')

    try:
        objectif_change_over = ObjectifChangeOver.objects.filter(
            ligne=ligne,
            client=client,
        ).last()

        type_changement_objectif = objectif_change_over.values.filter(
            changement__description__icontains=changement).first()

        response = {
            'success': True,
            'obi': type_changement_objectif.valeur,
        }
    except ObjectifChangeOver.DoesNotExist:
        response = {
            'success': False,
            'obi': ''
        }

    return JsonResponse(response)


def handle_form_submission(request, form_class, redirect_url):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            instance = form.save()
            new_entry = serializers.serialize('json', [instance])
            return JsonResponse({'success': True, 'message': 'Élément ajouté avec succès.', 'new_entry': new_entry})
        else:
            return JsonResponse({'success': False, 'message': 'Formulaire invalide.'})
    return redirect(redirect_url)


def saisir_temps_de_cycle(request):
    if request.method == 'POST':
        form = TempsDeCycleForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Temps de cycle ajouté avec succès.'})
        else:
            return JsonResponse({'success': False, 'message': 'Formulaire invalide.'})
    else:
        form = TempsDeCycleForm()
    context = {
        'form': form,
        'produit_form': ProduitForm(),
        'ligne_form': LigneForm(),
        'secteur_form': SecteurForm(),
        'client_form': ClientForm(),
        'equipe_form': EquipeForm(),
        'arret_form': ArretSimpleForm(),
        'subtype_arret_form': SubTypeArretForm(),
        'detail_subtype_arret_form': DetailSubTypeArretForm(),
        'moyen_form': MoyenForm(),
    }
    return render(request, 'create/saisir_temps_de_cycle.html', context=context)


def ajouter_produit(request):
    return handle_form_submission(request, ProduitForm, 'saisir_temps_de_cycle')


def ajouter_ligne(request):
    return handle_form_submission(request, LigneForm, 'saisir_temps_de_cycle')


def ajouter_secteur(request):
    return handle_form_submission(request, SecteurForm, 'saisir_temps_de_cycle')


def ajouter_client(request):
    return handle_form_submission(request, ClientForm, 'saisir_temps_de_cycle')


def ajouter_equipe(request):
    return handle_form_submission(request, EquipeForm, 'saisir_temps_de_cycle')


def ajouter_arret(request):
    return handle_form_submission(request, ArretSimpleForm, 'saisir_temps_de_cycle')


def ajouter_subtype_arret(request):
    return handle_form_submission(request, SubTypeArretForm, 'saisir_temps_de_cycle')


def ajouter_detail_subtype_arret(request):
    return handle_form_submission(request, DetailSubTypeArretForm, 'saisir_temps_de_cycle')


def ajouter_moyen(request):
    return handle_form_submission(request, MoyenForm, 'saisir_temps_de_cycle')


def index_report(request):
    return render(request, 'create/index_report.html')


def generate_report_form(request, report_type):
    form = ReportForm(report_type=report_type)

    if report_type == 'daily_line':
        form.fields['ligne'].required = True
        form.fields['secteur'].widget = forms.HiddenInput()
        form.fields['date'].widget = forms.Select(choices=get_dates_for_ligne())
    elif report_type == 'weekly_line':
        form.fields['ligne'].required = True
        form.fields['secteur'].widget = forms.HiddenInput()
        form.fields['date'].widget = forms.Select(choices=get_weeks_for_ligne_or_secteur())
    elif report_type == 'weekly_sector':
        form.fields['secteur'].required = True
        form.fields['ligne'].widget = forms.HiddenInput()
        form.fields['date'].widget = forms.Select(choices=get_weeks_for_ligne_or_secteur())
    elif report_type == 'monthly_sector':
        form.fields['secteur'].required = True
        form.fields['ligne'].widget = forms.HiddenInput()
        form.fields['date'].widget = forms.Select(choices=get_months_for_secteur())

    context = {
        'form': form,
        'report_type': report_type
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('create/report_form.html', context, request=request)
        return JsonResponse({'form_html': html})

    return render(request, 'create/index_report.html', context)


def generate_daily_line_pdf(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            ligne = form.cleaned_data['ligne']
            date = form.cleaned_data['date']

            productions = Production.objects.filter(ligne=ligne, date_production__date=date)

            if not productions.exists():
                return HttpResponse("Aucune production trouvée pour cette date et cette ligne.")

            # Calculer les valeurs agrégées
            temps_ouverture = sum(p.sum_temps_ouverture() for p in productions)
            tuf = sum(p.calculate_tu() for p in productions)
            arrets = productions.aggregate(
                total=ExpressionWrapper(
                    Coalesce(Sum('arretdeproduction__duree_en_heure'), 0) +
                    Coalesce(Sum('arretdeproduction__duree_en_minute'), 0) / 60,
                    output_field=FloatField()
                )
            )['total'] or 0

            tr = sum(p.calculate_tr() for p in productions)
            tf = sum(p.calculate_tf(p.calculate_tr()) for p in productions)
            ecart_cadence = sum(p.calculate_ecart_de_cadence(p.calculate_tf(p.calculate_tr())) for p in productions)
            trg = sum(p.calculate_trs() for p in productions) / len(productions) if productions else 0

            # Désengagements, Arrêts Propres et Arrêts Induits
            arrets_data = {
                'desengagements': get_arrets_data(productions, "engagement"),
                'arrets_propres': get_arrets_data(productions, "propre"),
                'arrets_induits': get_arrets_data(productions, "induit")
            }

            # Détails des données par Produit
            details_produits = get_product_details(productions)

            context = {
                'secteur': productions.first().secteur.nom_secteur if productions else "",
                'date': date,
                'ligne': ligne.nom,
                'temps_ouverture': format_value(temps_ouverture),
                'tuf': format_value(tuf),
                'arrets': format_value(arrets),
                'ecart_cadence': format_value(ecart_cadence),
                'ecart_cadence_percentage': format_value(
                    ((ecart_cadence / temps_ouverture) * 100) if temps_ouverture else 0),
                'trg': format_value(trg),
                'arrets_data': arrets_data,
                'details_produits': details_produits
            }

            # Générer le PDF
            template = get_template('create/daily_line_report.html')
            html = template.render(context)

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="rapport_journalier_{ligne.nom}_{date}.pdf"'

            pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), response)

            if not pdf.err:
                return response

            return HttpResponse("Erreur lors de la génération du PDF")

    return HttpResponse("Méthode non autorisée")


def generate_horizontal_bar_chart(data, title, file_path):
    # Trier les données par durée décroissante
    sorted_data = sorted(data, key=lambda x: x['duree'], reverse=True)

    # Calculer la hauteur de la figure en fonction du nombre d'éléments
    fig_height = max(6, len(sorted_data) * 0.5)

    fig, ax = plt.subplots(figsize=(12, fig_height))

    if sorted_data:
        bars = ax.barh([item['subtype_arret__description'] for item in sorted_data],
                       [item['duree'] for item in sorted_data],
                       height=0.5)

        ax.set_title(title)
        ax.set_xlabel('Durée (heures)')
        ax.set_ylabel('Sous-type d\'arrêt')

        ax.tick_params(axis='y', labelsize=8)

        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height() / 2, f'{width:.2f}',
                    ha='left', va='center', fontsize=8, fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'No data available', horizontalalignment='center', verticalalignment='center')

    plt.tight_layout()
    plt.savefig(file_path, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)

    return file_path


def generate_bar_chart(data, title, file_path):
    # Trier les données par durée décroissante
    sorted_data = sorted(data, key=lambda x: x['duree'], reverse=True)

    # Calculer la hauteur de la figure en fonction du nombre d'éléments
    fig_height = max(6, len(sorted_data) * 0.5)

    fig, ax = plt.subplots(figsize=(12, fig_height))

    if sorted_data:
        bars = ax.barh([item['moyen__nom'] for item in sorted_data],
                       [item['duree'] for item in sorted_data],
                       height=0.5)

        ax.set_title(title)
        ax.set_xlabel('Durée (heures)')
        ax.set_ylabel('Équipement')

        ax.tick_params(axis='y', labelsize=8)

        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height() / 2, f'{width:.2f}',
                    ha='left', va='center', fontsize=8, fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'No data available', horizontalalignment='center', verticalalignment='center')

    plt.tight_layout()
    plt.savefig(file_path, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)

    return file_path


def generate_weekly_line_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, report_type='weekly_line')
        if form.is_valid():
            ligne = form.cleaned_data['ligne']
            date = form.cleaned_data['date']

            timezone = pytz.timezone(settings.TIME_ZONE)

            # Convert date to datetime
            date = datetime.combine(date, datetime.min.time())
            start_of_week = timezone.localize(date - timedelta(days=date.weekday()))
            end_of_week = start_of_week + timedelta(days=6)

            productions = Production.objects.filter(
                ligne=ligne,
                date_production__range=[start_of_week, end_of_week]
            )

            if not productions.exists():
                return HttpResponse('Aucune donnée de production trouvée pour la période sélectionnée.', status=404)

            tu = sum(p.calculate_tu() for p in productions)
            to = sum(p.sum_temps_ouverture() for p in productions)
            tr = sum(p.calculate_tr() for p in productions)
            tf = sum(p.calculate_tf(p.calculate_tr()) for p in productions)
            tn = sum(p.calculate_tn(p.calculate_tf(p.calculate_tr()),
                                    p.calculate_ecart_de_cadence(p.calculate_tf(p.calculate_tr()))) for p in
                     productions)

            taux_qualite = (tu / tn) * 100 if tn else 0
            taux_performance = (tn / tf) * 100 if tf else 0
            disponibilite_operationnelle = (tf / tr) * 100 if tr else 0
            taux_strategie_engagement = (tr / to) * 100 if to else 0
            taux_charge = (tr / to) * 100 if to else 0

            trs = (taux_qualite * taux_performance * disponibilite_operationnelle) / 10000

            ecart_cadence = sum(p.calculate_ecart_de_cadence(p.calculate_tf(p.calculate_tr())) for p in productions)
            desengagement = sum(p.sum_desengagement() for p in productions)
            arrets_propres = sum(p.sum_arret_propre() for p in productions)
            arrets_induits = sum(p.sum_arret_induit() for p in productions)
            non_qualite = sum(p.sum_non_qualite() for p in productions)

            # Générer et sauvegarder les graphiques
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_charts')
            os.makedirs(temp_dir, exist_ok=True)

            desengagement_chart_path = os.path.join(temp_dir,
                                                    f"desengagement_{ligne.nom}_{start_of_week.strftime('%Y-%W')}.png")
            generate_horizontal_bar_chart(
                get_arrets_data(productions, "engagement"),
                "Désengagement des moyens (Heures)",
                desengagement_chart_path
            )

            arrets_induits_chart_path = os.path.join(temp_dir,
                                                     f"arrets_induits_{ligne.nom}_{start_of_week.strftime('%Y-%W')}.png")
            generate_horizontal_bar_chart(
                get_arrets_data(productions, "induit"),
                "Les Arrêts Induits (Heures)",
                arrets_induits_chart_path
            )

            arrets_propres_chart_path = os.path.join(temp_dir,
                                                     f"arrets_propres_{ligne.nom}_{start_of_week.strftime('%Y-%W')}.png")
            generate_horizontal_bar_chart(
                get_arrets_data(productions, "propre"),
                "Les Arrêts Propres (Heures)",
                arrets_propres_chart_path
            )

            pannes_equipement_chart_path = os.path.join(temp_dir,
                                                        f"pannes_equipement_{ligne.nom}_{start_of_week.strftime('%Y-%W')}.png")
            generate_bar_chart(
                get_pannes_equipement_data(productions),
                "Pareto des pannes par Equipement (Heures)",
                pannes_equipement_chart_path
            )

            # Vérifier si les fichiers ont été créés
            for chart_path in [desengagement_chart_path, arrets_induits_chart_path, arrets_propres_chart_path,
                               pannes_equipement_chart_path]:
                if not os.path.exists(chart_path):
                    print(f"Le fichier {chart_path} n'a pas été créé.")

            context = {
                'ligne': ligne,
                'semaine': start_of_week.strftime('%Y-%W'),
                'trs': trs,
                'tu': tu,
                'to': to,
                'tr': tr,
                'tf': tf,
                'tn': tn,
                'taux_qualite': taux_qualite,
                'taux_performance': taux_performance,
                'disponibilite_operationnelle': disponibilite_operationnelle,
                'taux_strategie_engagement': taux_strategie_engagement,
                'taux_charge': taux_charge,
                'ecart_cadence': ecart_cadence,
                'desengagement': desengagement,
                'arrets_propres': arrets_propres,
                'arrets_induits': arrets_induits,
                'non_qualite': non_qualite,
                'desengagement_chart': desengagement_chart_path,
                'arrets_induits_chart': arrets_induits_chart_path,
                'arrets_propres_chart': arrets_propres_chart_path,
                'pannes_equipement_chart': pannes_equipement_chart_path,
            }

            template = get_template('reports/weekly_line_report.html')
            html = template.render(context)

            response = HttpResponse(content_type='application/pdf')
            response[
                'Content-Disposition'] = f'inline; filename="rapport_hebdo_{ligne.nom}_{start_of_week.strftime("%Y-%W")}.pdf"'

            # Créer le PDF
            pisa_status = pisa.CreatePDF(html, dest=response)

            if pisa_status.err:
                return HttpResponse('Une erreur est survenue lors de la création du PDF', status=500)

            return response

        return HttpResponse('Méthode non autorisée', status=405)


@login_required
def generate_weekly_sector_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, report_type='weekly_sector')
        if form.is_valid():
            secteur = form.cleaned_data['secteur']
            date = form.cleaned_data['date']

            start_of_week = date - timedelta(days=date.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            productions = Production.objects.filter(
                secteur=secteur,
                date_production__range=[start_of_week, end_of_week]
            )

            if not productions.exists():
                return HttpResponse('Aucune donnée de production trouvée pour la période sélectionnée.', status=404)

            # Calcul des indicateurs globaux
            tu = sum(p.calculate_tu() for p in productions)
            to = sum(p.sum_temps_ouverture() for p in productions)
            tr = sum(p.calculate_tr() for p in productions)
            tf = sum(p.calculate_tf(p.calculate_tr()) for p in productions)
            tn = sum(p.calculate_tn(p.calculate_tf(p.calculate_tr()),
                                    p.calculate_ecart_de_cadence(p.calculate_tf(p.calculate_tr()))) for p in
                     productions)

            taux_qualite = (tu / tn) * 100 if tn else 0
            taux_performance = (tn / tf) * 100 if tf else 0
            disponibilite_operationnelle = (tf / tr) * 100 if tr else 0
            taux_strategie_engagement = (tr / to) * 100 if to else 0
            taux_charge = (tr / to) * 100 if to else 0

            trs = (taux_qualite * taux_performance * disponibilite_operationnelle) / 10000

            ecart_cadence = sum(p.calculate_ecart_de_cadence(p.calculate_tf(p.calculate_tr())) for p in productions)
            desengagement = sum(p.sum_desengagement() for p in productions)
            arrets_propres = sum(p.sum_arret_propre() for p in productions)
            arrets_induits = sum(p.sum_arret_induit() for p in productions)
            non_qualite = sum(p.sum_non_qualite() for p in productions)

            # Génération des graphiques
            desengagement_chart = generate_bar_chart2(get_arrets_data(productions, "engagement"),
                                                      "Désengagement des moyens (Heures)")
            arrets_induits_chart = generate_bar_chart2(get_arrets_data(productions, "induit"),
                                                       "Les Arrêts Induits (Heures)")
            arrets_propres_chart = generate_bar_chart2(get_arrets_data(productions, "propre"),
                                                       "Les Arrêts Propres (Heures)")
            pannes_equipement_chart = generate_bar_chart2(get_pannes_equipement_data(productions),
                                                          "Pareto des pannes par Equipement (Heures)")

            context = {
                'secteur': secteur,
                'semaine': start_of_week.strftime('%Y-%W'),
                'trs': format_value(trs),
                'tu': format_value(tu),
                'to': format_value(to),
                'tr': format_value(tr),
                'tf': format_value(tf),
                'tn': format_value(tn),
                'taux_qualite': format_value(taux_qualite),
                'taux_performance': format_value(taux_performance),
                'disponibilite_operationnelle': format_value(disponibilite_operationnelle),
                'taux_strategie_engagement': format_value(taux_strategie_engagement),
                'taux_charge': format_value(taux_charge),
                'ecart_cadence': format_value(ecart_cadence),
                'desengagement': format_value(desengagement),
                'arrets_propres': format_value(arrets_propres),
                'arrets_induits': format_value(arrets_induits),
                'non_qualite': format_value(non_qualite),
                'desengagement_chart': desengagement_chart,
                'arrets_induits_chart': arrets_induits_chart,
                'arrets_propres_chart': arrets_propres_chart,
                'pannes_equipement_chart': pannes_equipement_chart,
            }

            template = get_template('reports/weekly_sector_report.html')
            html = template.render(context)

            # Génération du PDF
            response = HttpResponse(content_type='application/pdf')
            response[
                'Content-Disposition'] = f'inline; filename="rapport_hebdo_secteur_{secteur.nom_secteur}_{start_of_week.strftime("%Y-%W")}.pdf"'

            pisa_status = pisa.CreatePDF(html, dest=response)

            if pisa_status.err:
                return HttpResponse('Une erreur est survenue lors de la création du PDF', status=500)

            return response

    else:
        form = ReportForm(report_type='weekly_sector')

    return render(request, 'reports/weekly_sector_report.html', {'form': form})


def generate_bar_chart2(data, title):
    plt.figure(figsize=(10, 6))
    plt.bar([item['subtype_arret__description'] for item in data], [item['duree'] for item in data])
    plt.title(title)
    plt.xlabel('Type d\'arrêt')
    plt.ylabel('Durée (heures)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    return graphic
