// Fonction pour afficher les messages (succès, erreur, chargement)
function displayMessage(message, type) {
    const messageContainer = document.getElementById('result');
    
    if (!messageContainer) {
        console.error("L'élément #result n'existe pas dans le DOM.");
        return;
    }

    messageContainer.innerHTML = '';  // Réinitialiser le message précédent
    messageContainer.style.display = 'block';  // S'assurer que la zone est visible

    // Appliquer un style en fonction du type de message (RAG)
    switch (type) {
        case 'success': // Green
            messageContainer.style.color = 'green';
            messageContainer.style.backgroundColor = '#e8f5e9'; // Vert clair
            break;
        case 'warning': // Amber (Jaune)
            messageContainer.style.color = 'orange';
            messageContainer.style.backgroundColor = '#fff3e0'; // Jaune clair
            break;
        case 'error': // Red
            messageContainer.style.color = 'red';
            messageContainer.style.backgroundColor = '#ffebee'; // Rouge clair
            break;
        case 'loading': // Blue
            messageContainer.style.color = 'blue';
            messageContainer.style.backgroundColor = '#e3f2fd'; // Bleu clair
            break;
    }

    // Ajouter le message dans le conteneur
    messageContainer.textContent = message;
    messageContainer.style.transition = 'opacity 0.5s ease-in-out';
}

// Fonction de validation du formulaire
function validateForm(data) {
    // Exemple de validation : vérifiez que tous les champs nécessaires sont remplis
    if (!data.nom || !data.prenom || !data.email || !data.age || !data.anciennete_permis || !data.puissance) {
        return 'Tous les champs doivent être remplis.';
    }

    // Validation de l'email
    const emailPattern = /^[^@]+@[^@]+\.[^@]+$/;
    if (!emailPattern.test(data.email)) {
        return 'L\'email est invalide.';
    }

    // Validation de l'âge (exemple: entre 18 et 100 ans)
    if (data.age < 18 || data.age > 100) {
        return 'L\'âge doit être compris entre 18 et 100.';
    }

    return null;  // Aucun problème de validation
}

// Attendre que le DOM soit complètement chargé avant d'ajouter l'événement
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('simulateur-form').addEventListener('submit', async function(e) {
        e.preventDefault();  // Empêche le rechargement de la page lors de la soumission du formulaire

        // Désactive le bouton pour éviter les soumissions multiples
        const submitButton = document.querySelector('.btn-submit');
        submitButton.disabled = true;

        // Récupère les données du formulaire
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());

        // Valider les données avant de soumettre
        const validationError = validateForm(data);
        if (validationError) {
            displayMessage(validationError, 'error');
            submitButton.disabled = false;
            return;
        }

        // Affiche un message de chargement pendant l'envoi des données
        displayMessage('Chargement...', 'loading');
        console.log('Envoi des données au serveur...');

        try {
            // Envoie des données au serveur via Fetch API
            const response = await fetch('/calcul_prime', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)  // Convertir les données du formulaire en JSON
            });

            // Vérifie si la réponse est correcte
            if (!response.ok) {
                throw new Error('Une erreur est survenue lors du calcul de la prime.');
            }

            // Récupère la réponse du serveur (JSON)
            const result = await response.json();
            console.log('Réponse du serveur:', result);

            // Affiche le résultat ou un message d'erreur
            if (result.error) {
                displayMessage(`Erreur: ${result.error}`, 'error');
                console.log('Erreur serveur:', result.error);
            } else {
                // Afficher la prime estimée dans le message de succès
                displayMessage(`Prime estimée: ${result.prime} MAD`, 'success');
                console.log('Prime estimée:', result.prime);
            }
        } catch (error) {
            // Gestion des erreurs liées à la requête
            console.error('Erreur:', error);
            displayMessage(`Erreur: ${error.message}`, 'error');
        } finally {
            // Réactive le bouton une fois le processus terminé
            submitButton.disabled = false;
        }
    });
});
