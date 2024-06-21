from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProduitCreationForm, ArretForm, ProductionDetailsForm
from .models import Ligne, SubTypeArret, DetailSubTypeArret, Production, Produit, Equipe, FaceProduit, Secteur, \
    TempsDeCycle, ProductionStepTwo, ArretDeProduction


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


def create_produit_step2(request):
    production_instance_id = request.session.get('production_instance_id')
    production_instance = Production.objects.get(id=production_instance_id)
    equipe_id = production_instance.equipe.id
    secteur_id = production_instance.secteur.id

    if not production_instance_id:
        return redirect('step1')

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
        'message': message,
        'message_type': message_type
    }
    return render(request, 'create/create_produit_step2.html', context=context)


def create_produit_step3(request):
    production_instance_id = request.session.get('production_instance_id')

    if request.GET.get('finish'):
        del request.session['production_instance_id']
        return redirect('step1')

    if not production_instance_id:
        return redirect('step1')

    production_instance = Production.objects.get(id=production_instance_id)
    production_step_two = ProductionStepTwo.objects.filter(production=production_instance).first()
    produit = production_step_two.produit
    client = production_step_two.client

    if request.method == 'POST':
        form = ArretForm(request.POST)
        if form.is_valid():
            arret = form.save(commit=False)
            arret.production = production_instance
            arret.save()

            print(production_step_two.calculate_fpy())
            print(production_step_two.temps_ouverture())
            print(production_step_two.total_arret())

            message = 'Arrêt ajouté avec succès'
            message_type = 'success'
        else:
            message = 'Formulaire invalide'
            message_type = 'danger'

        return JsonResponse({'success': message, 'message_type': message_type})

    else:
        form = ArretForm()
        message = None
        message_type = None

    context = {
        'form': form,
        'production_instance': production_instance,
        'message': message,
        'message_type': message_type,
        'produit': produit,
        'client': client
    }

    return render(request, 'create/create_produit_step3.html', context=context)


def load_products(request):
    client_id = request.GET.get('client_id')
    products = Produit.objects.filter(client_id=client_id).values('id', 'name')
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


def load_tcm(request):
    secteur_id = request.GET.get('secteur_id')
    produit_id = request.GET.get('produit_id')
    face_id = request.GET.get('face_id')

    try:
        tcm = TempsDeCycle.objects.get(secteur_id=secteur_id, produit_id=produit_id, face_id=face_id).tcm
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
