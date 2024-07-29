# Industrial Production Tracker 🚀

![CIPI ACTIA Logo](https://github.com/Abusooma/industrial-production-tracker/blob/main/actia4.png)

## 📄 Description

Industrial Production Tracker est une application web développée avec Django pour gérer et suivre la production de cartes magnétiques dans un environnement industriel. L'application permet la saisie, le suivi et l'analyse des données de production, ainsi que la génération de rapports détaillés avec des graphiques.

## ✨ Fonctionnalités

- 📝 Saisie des données de production (ligne, secteur, date, produits, temps de cycle)
- 🚫 Enregistrement des arrêts de production
- 📊 Consultation des données
- 🗂️ Génération de rapports PDF avec graphiques
- 💻 Interface utilisateur fluide avec AJAX

## 🛠️ Technologies

- 🔙 Backend : Django (Python)
- 🌐 Frontend : HTML, CSS, JavaScript
- 🗄️ Base de données : SQLite
- 🔄 AJAX pour les interactions asynchrones
- 📈 Matplotlib pour les graphiques
- 📝 ReportLab pour les rapports PDF

## ⚙️ Installation

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

## 🗂️ Structure du projet

```
industrial-production-tracker/
├── production_app/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── utils.py
├── templates/
│   └── production_app/
├── static/
│   ├── css/
│   └── js/
└── manage.py
```

## 📸 Captures d'écran

![Page d'accueil](https://github.com/Abusooma/industrial-production-tracker/blob/main/acti1.png)
*Page d'accueil*

![Formulaire de saisie](/path/to/input_form_screenshot.png)
*Formulaire de saisie des données de production*

## 👤 Auteur

Aboubacar Soumah - soumahaboubacarsopra@gmail.com
