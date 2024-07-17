from django import forms
from datetime import datetime, date
from .models import Ligne, Production, SubTypeArret, DetailSubTypeArret, ArretDeProduction, FaceProduit, \
    ProductionStepTwo, Moyen, TempsDeCycle, ObjectifChangeOver, TypeDeChangementDeObjectif, Produit, Client, Equipe, \
    Secteur, Arret, Famille


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['code_ac', 'famille', 'client']
        widgets = {
            'code_ac': forms.TextInput(attrs={'class': 'form-control'}),
            'famille': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'})
        }


class SecteurForm(forms.ModelForm):
    class Meta:
        model = Secteur
        fields = ['nom_secteur']
        widgets = {
            'nom_secteur': forms.TextInput(attrs={'class': 'form-control'}),
        }


class LigneForm(forms.ModelForm):
    class Meta:
        model = Ligne
        fields = ['secteur', 'nom']
        widgets = {
            'secteur': forms.Select(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ArretSimpleForm(forms.ModelForm):
    class Meta:
        model = Arret
        fields = ['nom', 'commentaire', 'heure_et_minute']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control'}),
            'heure_et_minute': forms.TimeInput(attrs={'class': 'form-control'}),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }


class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MoyenForm(forms.ModelForm):
    class Meta:
        model = Moyen
        fields = ['ligne', 'subtype_arret', 'nom']
        widgets = {
            'ligne': forms.Select(attrs={'class': 'form-control'}),
            'subtype_arret': forms.Select(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control'}),
        }


class SubTypeArretForm(forms.ModelForm):
    class Meta:
        model = SubTypeArret
        fields = ['arret', 'description']
        widgets = {
            'arret': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DetailSubTypeArretForm(forms.ModelForm):
    class Meta:
        model = DetailSubTypeArret
        fields = ['arret', 'sub_type_arret', 'description']
        widgets = {
            'arret': forms.Select(attrs={'class': 'form-control'}),
            'sub_type_arret': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProduitCreationForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = ['secteur', 'ligne', 'date_production', 'nombre_operateur', 'equipe']
        widgets = {
            'secteur': forms.Select(attrs={'class': 'form-control'}),
            'ligne': forms.Select(attrs={'class': 'form-control'}),
            'equipe': forms.Select(attrs={'class': 'form-control'}),
            'date_production': forms.DateInput(attrs={'class': 'form-control', 'id': 'id_date_production'}),
            'nombre_operateur': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ligne'].queryset = Ligne.objects.none()

        if 'secteur' in self.data:
            try:
                secteur_id = int(self.data.get('secteur'))
                self.fields['ligne'].queryset = Ligne.objects.filter(secteur_id=secteur_id).order_by('nom')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['ligne'].queryset = self.instance.secteur.ligne_set.order_by('nom')


class ProductionDetailsForm(forms.ModelForm):
    class Meta:
        model = ProductionStepTwo
        fields = ['produit', 'client', 'face_du_produit',
                  'heure_debut', 'heure_fin', 'quantity_fs', 'quantity_fc', 'defaults']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'quantity_fs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Inserez la quantite fs'}),
            'quantity_fc': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Inserez la quantite fc'}),
            'defaults': forms.NumberInput(attrs={'class': 'form-control'}),
            'face_du_produit': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        secteur_id = kwargs.pop('secteur_id', None)
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.secteur:
            secteur_id = self.instance.secteur.id

        if secteur_id:
            self.fields['face_du_produit'].queryset = FaceProduit.objects.filter(secteur_id=secteur_id)
        else:
            self.fields['face_du_produit'].queryset = FaceProduit.objects.none()

        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['produit'].queryset = Produit.objects.filter(client_id=client_id).order_by('code_ac')
            except (ValueError, TypeError):
                pass

        elif self.instance.pk:
            self.fields['produit'].queryset = self.instance.ligne.produit_set.order_by('code_ac')

        else:
            self.fields['produit'].queryset = Produit.objects.none()


class ArretForm(forms.ModelForm):
    duree_en_heure = forms.IntegerField(label='Heures', required=False)
    duree_en_minute = forms.IntegerField(label='Minutes', required=False)

    class Meta:
        model = ArretDeProduction
        fields = ['type_arret', 'subtype_arret', 'detail_sub_type_arret', 'moyen', 'commentaire', 'duree_en_heure',
                  'duree_en_minute', 'changement', 'intervenant', 'action']

        widgets = {
            'type_arret': forms.Select(attrs={'class': 'form-control'}),
            'subtype_arret': forms.Select(attrs={'class': 'form-control'}),
            'detail_sub_type_arret': forms.Select(attrs={'class': 'form-control'}),
            'moyen': forms.Select(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'changement': forms.Select(attrs={'class': 'form-control'}),
            'intervenant': forms.Select(attrs={'class': 'form-control'}),
            'action': forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
        }

    def __init__(self, *args, **kwargs):
        ligne_id = kwargs.pop('ligne_id', None)
        super().__init__(*args, **kwargs)
        self.fields['subtype_arret'].queryset = SubTypeArret.objects.none()
        self.fields['detail_sub_type_arret'].queryset = DetailSubTypeArret.objects.none()

        if 'type_arret' in self.data:
            try:
                type_arret_id = int(self.data.get('type_arret'))
                self.fields['subtype_arret'].queryset = SubTypeArret.objects.filter(arret_id=type_arret_id).order_by(
                    'description')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['subtype_arret'].queryset = self.instance.type_arret.subtypearret_set.order_by('description')

        if 'subtype_arret' in self.data:
            try:
                subtype_arret_id = int(self.data.get('subtype_arret'))
                self.fields['detail_sub_type_arret'].queryset = DetailSubTypeArret.objects.filter(
                    sub_type_arret_id=subtype_arret_id).order_by('description')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['detail_sub_type_arret'].queryset = self.instance.subtype_arret.detailsubtypearret_set.order_by(
                'description')

        if 'subtype_arret' in self.data:
            try:
                subtype_arret_name = SubTypeArret.objects.get(id=int(self.data.get('subtype_arret'))).description
                if subtype_arret_name == 'Panne':
                    self.fields['moyen'].widget.attrs.update({'style': 'display: block;'})
                else:
                    self.fields['moyen'].widget.attrs.update({'style': 'display: none;'})
            except (ValueError, TypeError, SubTypeArret.DoesNotExist):
                pass

        if self.instance.pk and self.instance.ligne:
            ligne_id = self.instance.ligne.id

        if ligne_id:
            self.fields['moyen'].queryset = Moyen.objects.filter(ligne_id=ligne_id)
        else:
            self.fields['moyen'].queryset = Moyen.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        heure = cleaned_data.get('duree_en_heure')
        minute = cleaned_data.get('duree_en_minute')

        if heure is None and minute is None:
            raise forms.ValidationError("Vous devez saisir au moins l'heure ou les minutes.")

        return cleaned_data


class TempsDeCycleForm(forms.ModelForm):
    class Meta:
        model = TempsDeCycle
        fields = ['ligne', 'client', 'produit', 'face', 'moyen', 'tcm', 'commentaire']
        widgets = {
            'ligne': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'face': forms.Select(attrs={'class': 'form-control'}),
            'moyen': forms.Select(attrs={'class': 'form-control'}),
            'tcm': forms.NumberInput(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control text-area-resize', 'rows': 5}),
        }
        labels = {
            'moyen': 'equipement menant'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['produit'].queryset = Produit.objects.filter(client_id=client_id).order_by('code_ac')
            except (ValueError, TypeError, Client.DoesNotExist):
                pass

        elif self.instance.pk:
            self.fields['produit'].queryset = self.instance.client.produit_set.order_by('code_ac')

        else:
            self.fields['produit'].queryset = Produit.objects.none()

        if 'ligne' in self.data:
            try:
                ligne_id = int(self.data.get('ligne'))
                self.fields['moyen'].queryset = Moyen.objects.filter(ligne_id=ligne_id).order_by('nom')
            except (ValueError, TypeError, Ligne.DoesNotExist):
                pass

        elif self.instance.pk:
            self.fields['moyen'].queryset = self.instance.ligne.moyen_set.order_by('nom')

        else:
            self.fields['moyen'].queryset = Moyen.objects.none()


class ObjectifChangeOverForm(forms.ModelForm):
    class Meta:
        model = ObjectifChangeOver
        fields = '__all__'
        widgets = {
            'secteur': forms.Select(attrs={'class': 'form-control'}),
            'ligne': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'famille': forms.Select(attrs={'class': 'form-control'})

        }
        labels = {
            'secteur': 'Secteur',
            'ligne': 'Ligne',
            'client': 'Client',
            'produit': 'Produit',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'secteur' in self.data:
            try:
                secteur_id = int(self.data.get('secteur'))
                self.fields['ligne'].queryset = Ligne.objects.filter(secteur_id=secteur_id).order_by('nom')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['ligne'].queryset = self.instance.secteur.ligne_set.order_by('nom')

        else:
            self.fields['ligne'].queryset = Ligne.objects.none()

        if 'famille' in self.data:
            try:
                famille_id = int(self.data.get('famille'))
                self.fields['produit'].queryset = Produit.objects.filter(famille_id=famille_id).order_by('code_ac')
            except (ValueError, TypeError, Famille.DoesNotExist):
                pass

        elif self.instance.pk:
            self.fields['produit'].queryset = self.instance.famille.produit_set.order_by('code_ac')

        else:
            self.fields['produit'].queryset = Produit.objects.none()


class TypeDeChangementDeObjectifForm(forms.ModelForm):
    class Meta:
        model = TypeDeChangementDeObjectif
        fields = ['changement', 'valeur']
        widgets = {
            'changement': forms.Select(attrs={'class': 'form-control'}),
            'valeur': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'changement': '',
            'valeur': 'Valeur',
        }


class CustomDateField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.date_format = kwargs.pop('date_format', '%Y-%m-%d')
        super().__init__(*args, **kwargs)

    def clean(self, value):
        if not value:
            return None
        try:
            if self.date_format == '%Y-%W':
                # Pour le format semaine
                year, week = map(int, value.split('-'))
                return date.fromisocalendar(year, week, 1)
            elif self.date_format == '%Y-%m':
                # Pour le format mois
                return datetime.strptime(value + '-01', '%Y-%m-%d').date()
            else:
                # Pour le format jour
                return datetime.strptime(value, self.date_format).date()
        except ValueError:
            raise forms.ValidationError('Format de date invalide.')


class ReportForm(forms.Form):
    ligne = forms.ModelChoiceField(
        queryset=Ligne.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control custom-select',
            'style': 'border: 2px solid #33333333; border-radius: 0.25rem; padding: 0.5rem;'
        })
    )
    secteur = forms.ModelChoiceField(
        queryset=Secteur.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control custom-select',
            'style': 'border: 2px solid #33333333; border-radius: 0.25rem; padding: 0.5rem;'
        })
    )
    date = CustomDateField(
        widget=forms.Select(attrs={
            'class': 'form-control custom-date',
            'style': 'border: 2px solid #33333333; border-radius: 0.25rem; padding: 0.5rem;'
        })
    )

    def __init__(self, *args, **kwargs):
        self.report_type = kwargs.pop('report_type', None)
        super().__init__(*args, **kwargs)
        if self.report_type:
            if self.report_type in ['weekly_line', 'weekly_sector']:
                self.fields['date'].date_format = '%Y-%W'
            elif self.report_type == 'monthly_sector':
                self.fields['date'].date_format = '%Y-%m'
