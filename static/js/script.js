$(document).ready(function() {
    // Fonction pour mettre à jour l'état actif des liens
    function updateActiveLinks(clickedLink) {
        // Supprimer la classe active de tous les liens de la navbar et de la sidebar
        $('.navbar-nav .nav-item .nav-link').removeClass('active');
        $('.sidebar-link').removeClass('active');

        // Ajouter la classe active uniquement au lien cliqué
        $(clickedLink).addClass('active');

        // Enregistrer l'URL du lien cliqué dans localStorage
        localStorage.setItem('activeLink', $(clickedLink).attr('href'));
    }

    // Récupérer l'URL active depuis localStorage au chargement de la page
    var activeLink = localStorage.getItem('activeLink');

    // Si une URL active existe, ajouter la classe active au lien correspondant
    if (activeLink) {
        $('.navbar-nav .nav-item .nav-link[href="' + activeLink + '"]').addClass('active');
        $('.sidebar-link[href="' + activeLink + '"]').addClass('active');
    }

    // Écouteur d'événement de clic pour chaque lien de menu dans la navbar
    $('.navbar-nav .nav-item .nav-link').click(function(e) {
        updateActiveLinks(this);
    });

    // Écouteur d'événement de clic pour chaque lien de la sidebar
    $('.sidebar-link').click(function(e) {
        updateActiveLinks(this);
    });
});
