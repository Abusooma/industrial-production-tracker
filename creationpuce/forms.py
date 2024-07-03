from django import forms
from .models import Ligne, Production, SubTypeArret, DetailSubTypeArret, ArretDeProduction, FaceProduit, \
    ProductionStepTwo, Moyen, TempsDeCycle


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
        fields = ['secteur', 'client', 'produit', 'face', 'equipement_menant', 'tcm', 'commentaire']
        widgets = {
            'secteur': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'face': forms.Select(attrs={'class': 'form-control'}),
            'equipement_menant': forms.Select(attrs={'class': 'form-control'}),
            'tcm': forms.NumberInput(attrs={'class': 'form-control'}),
            'commentaire': forms.TextInput(attrs={'class': 'form-control'}),
        }
