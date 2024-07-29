# Industrial Production Tracker

![CIPI ACTIA Logo](/path/to/logo.png)

## Description du projet

Industrial Production Tracker est une application web développée avec Django pour gérer et suivre la production de cartes magnétiques dans un environnement industriel. Cette application permet la saisie, le suivi et l'analyse des données de production, ainsi que la génération de rapports détaillés avec des visualisations graphiques.

## Fonctionnalités principales

- Saisie des données de production (ligne, secteur, date, produits, temps de cycle)
- Enregistrement des arrêts de production
- Consultation des données saisies
- Génération de rapports PDF incluant des graphiques (utilisant matplotlib) :
  - Rapport de production journalier par ligne
  - Rapport hebdomadaire par ligne
  - Rapport hebdomadaire par semaine
  - Rapport mensuel par secteur
- Interface utilisateur intuitive avec des requêtes AJAX pour une expérience fluide

## Technologies utilisées

- Backend : Django (Python)
- Frontend : HTML, CSS, JavaScript
- Base de données : SQLite (par défaut avec Django)
- AJAX pour les interactions asynchrones
- Matplotlib pour la génération de graphiques
- ReportLab pour la création de rapports PDF
- Packages Python pour le formatage des dates

## Installation et configuration

```bash
# Cloner le dépôt
git clone https://github.com/Abusooma/industrial-production-tracker.git
cd industrial-production-tracker

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`

# Installer les dépendances
pip install -r requirements.txt

# Effectuer les migrations
python manage.py migrate

# Lancer le serveur de développement
python manage.py runserver
```

## Structure du projet

```
industrial-production-tracker/
│
├── production_app/
│   ├── models.py          # Définition des modèles de données
│   ├── views.py           # Logique de traitement des vues
│   ├── forms.py           # Formulaires pour la saisie des données
│   └── utils.py           # Fonctions utilitaires (génération de rapports, etc.)
│
├── templates/
│   └── production_app/    # Templates HTML pour l'interface utilisateur
│
├── static/
│   ├── css/               # Feuilles de style CSS
│   └── js/                # Scripts JavaScript pour les interactions AJAX
│
└── manage.py              # Script de gestion Django
```

## Captures d'écran

![Page d'accueil](/path/to/homepage_screenshot.png)
*Page d'accueil montrant les différents secteurs de production*

![Formulaire de saisie](/path/to/input_form_screenshot.png)
*Formulaire de saisie des données de production*

## Défis surmontés

1. Implémentation d'un système de calcul précis pour les métriques de production
2. Intégration de Matplotlib avec Django pour générer des graphiques dynamiques dans les rapports PDF
3. Optimisation des requêtes de base de données pour gérer efficacement de grandes quantités de données de production
4. Création d'une interface utilisateur réactive avec AJAX pour une saisie de données fluide sans rechargement de page

## Fonctionnalités futures

- Intégration avec des systèmes ERP pour une synchronisation des données en temps réel
- Mise en place d'un tableau de bord en temps réel pour le suivi de la production
- Ajout de fonctionnalités d'analyse prédictive pour anticiper les problèmes de production
- Développement d'une API RESTful pour permettre l'intégration avec d'autres systèmes

## Contribution

Ce projet est actuellement un projet personnel et n'est pas ouvert aux contributions externes. Cependant, les retours et suggestions sont les bienvenus via les issues GitHub.

## Auteur

[Votre Nom] - [Votre Email]

## Licence

Ce projet est sous licence [insérer le type de licence ici, par exemple MIT License]. Voir le fichier `LICENSE` pour plus de détails.
