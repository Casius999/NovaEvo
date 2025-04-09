import os
import stripe
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration de Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")

# Initialisation de Flask, SQLAlchemy et Flask-Login
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "votre_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_PATH", 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Modèle utilisateur
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    stripe_customer_id = db.Column(db.String(100))
    subscription_id = db.Column(db.String(100))
    subscription_status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Configuration de Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def register_user(email: str, password: str, name: str = None) -> User:
    """
    Inscription d'un nouvel utilisateur
    
    Args:
        email: Adresse email de l'utilisateur
        password: Mot de passe de l'utilisateur
        name: Nom de l'utilisateur (optionnel)
    
    Returns:
        User: L'objet utilisateur créé
    """
    # Vérifier si l'utilisateur existe déjà
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {"error": "Un utilisateur avec cet email existe déjà."}
    
    # Créer un nouvel utilisateur
    user = User(email=email, name=name)
    user.set_password(password)
    
    # Créer un client Stripe
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name
        )
        user.stripe_customer_id = customer.id
    except Exception as e:
        return {"error": f"Erreur lors de la création du client Stripe: {str(e)}"}
    
    # Sauvegarder l'utilisateur
    db.session.add(user)
    db.session.commit()
    
    return user

def login_user_credentials(email: str, password: str):
    """
    Authentifie un utilisateur
    
    Args:
        email: Adresse email de l'utilisateur
        password: Mot de passe de l'utilisateur
    
    Returns:
        User: L'objet utilisateur authentifié ou None
    """
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        login_user(user)
        return user
    return None

def create_subscription(customer_id: str, plan_id: str = "plan_basic") -> dict:
    """
    Crée un abonnement Stripe
    
    Args:
        customer_id: ID du client Stripe
        plan_id: ID du plan d'abonnement (par défaut: plan_basic)
    
    Returns:
        dict: Les détails de l'abonnement créé
    """
    try:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": plan_id}],
            expand=["latest_invoice.payment_intent"]
        )
        
        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "current_period_end": subscription.current_period_end,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice else None
        }
    except Exception as e:
        return {"error": f"Erreur lors de la création de l'abonnement: {str(e)}"}

def cancel_subscription(subscription_id: str) -> dict:
    """
    Annule un abonnement
    
    Args:
        subscription_id: ID de l'abonnement Stripe
    
    Returns:
        dict: Résultat de l'annulation
    """
    try:
        subscription = stripe.Subscription.delete(subscription_id)
        return {
            "status": "success",
            "subscription_id": subscription_id,
            "canceled_at": subscription.canceled_at
        }
    except Exception as e:
        return {"error": f"Erreur lors de l'annulation de l'abonnement: {str(e)}"}

def get_subscription(subscription_id: str) -> dict:
    """
    Récupère les détails d'un abonnement
    
    Args:
        subscription_id: ID de l'abonnement Stripe
    
    Returns:
        dict: Détails de l'abonnement
    """
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "current_period_start": subscription.current_period_start,
            "current_period_end": subscription.current_period_end,
            "plan": subscription.items.data[0].price.id if subscription.items.data else None
        }
    except Exception as e:
        return {"error": f"Erreur lors de la récupération de l'abonnement: {str(e)}"}

def process_subscription(user_data: dict) -> dict:
    """
    Traite l'inscription et la souscription d'un utilisateur
    
    Args:
        user_data: Dictionnaire contenant les informations de l'utilisateur
            - email: Email de l'utilisateur
            - password: Mot de passe
            - name: Nom (optionnel)
            - plan_id: ID du plan d'abonnement (optionnel, par défaut: plan_basic)
    
    Returns:
        dict: Résultat du traitement
    """
    # Vérifier si l'utilisateur existe
    user = User.query.filter_by(email=user_data['email']).first()
    
    # Si l'utilisateur n'existe pas, l'inscrire
    if not user:
        result = register_user(user_data['email'], user_data['password'], user_data.get('name'))
        if isinstance(result, dict) and "error" in result:
            return result
        user = result
    else:
        # Vérifier le mot de passe
        if not user.check_password(user_data['password']):
            return {"status": "error", "message": "Mot de passe incorrect."}
        
        # Connecter l'utilisateur
        login_user(user)

    # Créer un client Stripe si nécessaire
    if not user.stripe_customer_id:
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name
            )
            user.stripe_customer_id = customer.id
            db.session.commit()
        except Exception as e:
            return {"status": "error", "message": f"Erreur lors de la création du client Stripe: {str(e)}"}

    # Plan par défaut
    plan_id = user_data.get('plan_id', "price_basic")  # ID du plan Stripe (19,90€/mois)

    # Vérifier si l'utilisateur a déjà un abonnement actif
    if user.subscription_id:
        subscription_details = get_subscription(user.subscription_id)
        if "error" not in subscription_details and subscription_details["status"] in ["active", "trialing"]:
            return {
                "status": "success",
                "message": "Vous avez déjà un abonnement actif.",
                "subscription_id": user.subscription_id,
                "subscription_status": subscription_details["status"]
            }

    # Créer l'abonnement
    try:
        subscription_result = create_subscription(user.stripe_customer_id, plan_id)
        
        if "error" in subscription_result:
            return {"status": "error", "message": subscription_result["error"]}
        
        # Mettre à jour les informations de l'utilisateur
        user.subscription_id = subscription_result["subscription_id"]
        user.subscription_status = subscription_result["status"]
        db.session.commit()
        
        return {
            "status": "success",
            "message": "Souscription créée avec succès.",
            "subscription_id": subscription_result["subscription_id"],
            "subscription_status": subscription_result["status"],
            "client_secret": subscription_result.get("client_secret")
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors de la création de la souscription: {str(e)}"}

def webhook_handler(payload, sig_header):
    """
    Traite les webhooks Stripe
    
    Args:
        payload: Le corps de la requête
        sig_header: L'en-tête de signature Stripe
    
    Returns:
        dict: Résultat du traitement
    """
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Payload invalide
        return {"status": "error", "message": "Payload invalide"}
    except stripe.error.SignatureVerificationError as e:
        # Signature invalide
        return {"status": "error", "message": "Signature invalide"}
        
    # Traiter l'événement
    if event.type == 'checkout.session.completed':
        session = event.data.object
        # Traiter le paiement réussi
        customer_id = session.customer
        subscription_id = session.subscription
        
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.subscription_id = subscription_id
            user.subscription_status = "active"
            db.session.commit()
    
    elif event.type == 'customer.subscription.updated':
        subscription = event.data.object
        # Mettre à jour le statut de l'abonnement
        customer_id = subscription.customer
        subscription_id = subscription.id
        status = subscription.status
        
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.subscription_status = status
            db.session.commit()
    
    elif event.type == 'customer.subscription.deleted':
        subscription = event.data.object
        # L'abonnement a été annulé ou a expiré
        customer_id = subscription.customer
        
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.subscription_status = "canceled"
            db.session.commit()
    
    return {"status": "success", "message": "Webhook traité avec succès"}

# Initialiser la base de données si le script est exécuté directement
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("Base de données initialisée avec succès.")
