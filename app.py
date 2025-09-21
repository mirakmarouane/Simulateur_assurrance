import logging
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import re  # Pour valider les emails

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://karim:Admin%40123@localhost:5432/simulateur_assurance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de SQLAlchemy et Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configuration du log
logging.basicConfig(level=logging.DEBUG)

# Modèle Utilisateur pour la base de données
class Utilisateur(db.Model):
    __tablename__ = 'utilisateur'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    age = db.Column(db.Integer)
    anciennete_permis = db.Column(db.Integer)
    puissance = db.Column(db.Integer)
    prime = db.Column(db.Numeric)  # Ajoutez cette ligne pour la colonne 'prime'

    def __repr__(self):
        return f"<Utilisateur {self.nom}>"

# Fonction pour valider l'email
def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

# Fonction pour valider l'âge
def is_valid_age(age):
    return isinstance(age, int) and 18 <= age <= 100

# Fonction pour valider les données
def is_valid_data(data):
    return is_valid_email(data['email']) and is_valid_age(int(data['age']))

# Route d'accueil - Affichage du formulaire
@app.route('/')
def index():
    return render_template('index.html')

# Fonction de calcul de la prime d'assurance
def calculer_prime(age, anciennete_permis, puissance, usage_type):
    app.logger.debug(f"Calcul de la prime avec les paramètres : âge={age}, anciennete_permis={anciennete_permis}, puissance={puissance}, usage_type={usage_type}")
    
    civil_liability = 300  # Coût de base

    # Facteurs de calcul
    age_factor = 1.6 - 0.02 * (25 - age) if age < 25 else (1.0 + 0.01 * (30 - abs(age - 30)) if age <= 60 else 1.3 + 0.015 * (age - 60))
    license_factor = max(0.85, 1.6 - 0.06 * anciennete_permis)
    vehicle_factor = 1.0 + 0.04 * min(anciennete_permis, 15)
    power_factor = 1.0 + 0.015 * puissance
    passenger_factor = 1.0 + 0.03 * max(0, 4 - 1)
    usage_factor = {'personal': 1.0, 'professional': 1.4}.get(usage_type, 1.15)

    # Calcul final
    multiplier = age_factor * license_factor * vehicle_factor * power_factor * passenger_factor * usage_factor
    app.logger.debug(f"Multiplicateur total : {multiplier}")
    total = civil_liability * multiplier
    app.logger.debug(f"Prime calculée : {total}")

    return total

# Route pour calculer la prime d'assurance
@app.route('/calcul_prime', methods=['POST'])
def calcul_prime():
    data = request.get_json()
    app.logger.debug(f"Données reçues du formulaire : {data}")

    # Validation des données
    if not is_valid_data(data):
        return jsonify({'error': 'Les données soumises sont invalides'}), 400

    try:
        # Extraction des valeurs
        age = int(data['age'])
        anciennete_permis_raw = data['anciennete_permis']
        puissance = int(data['puissance'])
        usage_type = data.get('usage_type', 'personal')

        # Mapping ancienneté permis
        anciennete_permis_map = {'moins_5': 5, '5_20': 10, 'plus_20': 20}
        anciennete_permis = anciennete_permis_map.get(anciennete_permis_raw, None)
        if anciennete_permis is None:
            app.logger.error(f"Ancienneté du permis invalide reçue : {anciennete_permis_raw}")
            return jsonify({'error': 'Ancienneté du permis invalide'}), 400

        # Calcul de la prime
        prime = calculer_prime(age, anciennete_permis, puissance, usage_type)

        # Sauvegarde en base
        utilisateur = Utilisateur(
            nom=data['nom'],
            prenom=data['prenom'],
            email=data['email'],
            age=age,
            anciennete_permis=anciennete_permis,
            puissance=puissance,
            prime=prime
        )
        db.session.add(utilisateur)
        db.session.commit()

        # Réponse JSON
        return jsonify({'prime': f'{prime:.2f}'}), 200

    except Exception as e:
        app.logger.exception("Erreur lors du calcul de la prime")  # Log l'erreur complète
        return jsonify({'error': f"Erreur dans le calcul de la prime: {str(e)}"}), 500

# Route simulateur
@app.route('/simulateur')
def simulateur():
    return render_template('simulateur.html')

# Lancement
if __name__ == "__main__":
    app.run(debug=True, port=5001)
