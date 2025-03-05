import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import logging

# -------------------------------------------------
# Configuration du dossier et du logger dédié pour le tracking
# -------------------------------------------------
# Déterminer le répertoire du script (la racine de votre projet)
script_directory = os.path.dirname(os.path.abspath(__file__))

# Dossier des logs (dans "Avis-email/logs")
log_directory = os.path.join(script_directory, "logs")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
tracking_log_path = os.path.join(log_directory, "tracking.log")

# Créer un logger dédié nommé "tracking" qui écrira uniquement dans le fichier tracking.log
tracking_logger = logging.getLogger("tracking")
tracking_logger.setLevel(logging.INFO)
# On empêche la propagation pour que ces logs n'apparaissent pas dans la console
tracking_logger.propagate = False

# Créer un FileHandler pour écrire dans tracking.log (mode append)
file_handler = logging.FileHandler(tracking_log_path, mode='a')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
tracking_logger.addHandler(file_handler)

# Test initial pour vérifier que le logger fonctionne
tracking_logger.info("==> Tracking logger initialisé.")

# Pour laisser apparaître le lien de démarrage, réglons le niveau du logger 'werkzeug' sur INFO
logging.getLogger('werkzeug').setLevel(logging.INFO)

# -------------------------------------------------
# Création de l'application Flask
# -------------------------------------------------
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Pour afficher des messages flash

# -------------------------------------------------
# Endpoints de Tracking
# -------------------------------------------------

# Endpoint pour le suivi des ouvertures d'email (pixel de tracking)
@app.route('/tracking/open')
def tracking_open():
    email = request.args.get('email')
    tracking_logger.info(f"Ouverture de mail par : {email}")
    # Utiliser un chemin dynamique pour accéder à l'image transparente dans le dossier static
    transparent_path = os.path.join(script_directory, 'static', 'transparent.png')
    return send_file(transparent_path, mimetype='image/png')

# Endpoint pour le suivi des clics sur les liens
@app.route('/click/<magasin>')
def click_tracking(magasin):
    email = request.args.get('email')
    tracking_logger.info(f"Clic sur le lien pour {magasin} par : {email}")
    # Selon le magasin, redirige vers l'URL finale
    if magasin.lower() == 'nancy':
        url_finale = "https://g.page/r/Ccz4I1-xV-mxEBM/review"
    elif magasin.lower() == 'metz':
        url_finale = "https://g.page/r/CYNztFt83QRGEBM/review"
    elif magasin.lower() == 'strasbourg':
        url_finale = "https://g.page/r/CaMB1keRh-NgEBM/review"
    else:
        url_finale = "https://meubleprive.fr"
    return redirect(url_finale)

# -------------------------------------------------
# Fonction pour envoyer les emails (votre programme de base)
# -------------------------------------------------
def envoyer_emails(fichier_csv):
    try:
        # Charger la base de données client depuis le fichier CSV
        df = pd.read_csv(fichier_csv, sep=';')

        # Liens d'avis Google (URL finale, ils ne seront pas utilisés directement dans l'e-mail)
        lien_avis_google_nancy = "https://g.page/r/Ccz4I1-xV-mxEBM/review"
        lien_avis_google_metz = "https://g.page/r/CYNztFt83QRGEBM/review"
        lien_avis_google_strasbourg = "https://g.page/r/CaMB1keRh-NgEBM/review"

        # Paramètres de l'e-mail
        sender_email = "contact@meubleprive.fr"
        password = "jepn enmw tbig bzzv"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Créer une session SMTP pour envoyer des e-mails
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)

        # Pour chaque client dans le CSV, envoyer un e-mail
        for index, row in df.iterrows():
            recipient_email = row['email']
            subject = "Profitez de -50% sur toutes les bougies et décorations !"
            
            # Pour intégrer le tracking, créer des liens qui pointent vers vos endpoints
            lien_tracking_nancy = f"http://127.0.0.1:5000/click/nancy?email={row['email']}"
            lien_tracking_metz = f"http://127.0.0.1:5000/click/metz?email={row['email']}"
            lien_tracking_strasbourg = f"http://127.0.0.1:5000/click/strasbourg?email={row['email']}"

            # Construire le corps de l'e-mail en utilisant les liens de tracking
            body = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        color: #000000 !important;
                        line-height: 1.6;
                        margin: 0;
                        padding: 0;
                        background-color: #f9f9f9;
                        text-align: center;
                    }}
                    a {{
                        color: #1a73e8 !important;
                        text-decoration: none;
                        font-weight: bold;
                    }}
                    h3 {{
                        color: #000000 !important;
                    }}
                    p {{
                        color: #000000 !important;
                        text-align: center;
                    }}
                    .content {{
                        max-width: 600px;
                        margin: 30px auto;
                        padding: 20px;
                        background-color: #ffffff;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        text-align: center;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background-color: #f50057;
                        color: #ffffff !important;
                        padding: 10px 20px;
                        border-radius: 25px;
                        font-size: 18px;
                        text-align: center;
                        margin-top: 20px;
                        text-decoration: none;
                    }}
                    .cta-button:hover {{
                        background-color: #d50047;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                    }}
                    .footer img {{
                        width: 350px;
                        height: auto;
                    }}
                    .image-container img {{
                        width: 100%;
                        max-width: 1000px;
                        height: auto;
                        border-radius: 10px;
                        margin-bottom: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="content">
                    <div class="image-container">
                        <img src="cid:products" alt="Produits" style="width: 100%; max-width: 500px; height: auto; border-radius: 10px;">
                    </div>
                    <h3>Bonjour {row['nom']},</h3>
                    <p>Merci d'avoir choisi <strong>Meuble Prive</strong> pour vos achats !</p>
                    <p>Votre avis est essentiel pour nous.</p>
                    <p>Pour vous remercier, nous vous offrons une remise exceptionnelle de 50% sur toutes les bougies et décorations.</p>
                    <p><em>Offre exclusive réservée aux clients fidèles.</em></p>
                    <p>Cliquez sur le lien correspondant à votre magasin pour laisser votre avis :</p>
                    <br><strong>Meuble Prive NANCY :</strong><br>
                    <a href="{lien_tracking_nancy}" target="_blank" class="cta-button">Laisser mon avis</a><br>
                    <br><strong>Meuble Prive METZ :</strong><br>
                    <a href="{lien_tracking_metz}" target="_blank" class="cta-button">Laisser mon avis</a><br>
                    <br><strong>Meuble Prive STRASBOURG :</strong><br>
                    <a href="{lien_tracking_strasbourg}" target="_blank" class="cta-button">Laisser mon avis</a>
                    <p>Merci pour votre confiance, à très bientôt,<br><strong>L’équipe Meuble Prive</strong></p>
                </div>
                <div class="footer">
                    <img src="cid:logo" alt="MeublePrive Logo">
                </div>
            </body>
            </html>
            """
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = recipient_email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'html'))

            # Utiliser des chemins dynamiques pour accéder aux images dans le dossier static
            product_image_path = os.path.join(script_directory, 'static', 'bougie-sapins-dans-la-brume-yankee-candle.jpg')
            with open(product_image_path, 'rb') as products_file:
                products_image = MIMEImage(products_file.read())
                products_image.add_header('Content-ID', '<products>')
                message.attach(products_image)

            logo_image_path = os.path.join(script_directory, 'static', '1.jpg')
            with open(logo_image_path, 'rb') as logo_file:
                logo = MIMEImage(logo_file.read())
                logo.add_header('Content-ID', '<logo>')
                message.attach(logo)

            server.sendmail(sender_email, recipient_email, message.as_string())
            flash(f"Email envoyé à {recipient_email}")
        server.quit()
        return True
    except Exception as e:
        return str(e)

# -------------------------------------------------
# Routes de l'interface
# -------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("Aucun fichier sélectionné", "danger")
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash("Aucun fichier sélectionné", "danger")
        return redirect(request.url)
    if file:
        # Créer le dossier uploads dans le répertoire du script
        uploads_dir = os.path.join(script_directory, 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        file_path = os.path.join(uploads_dir, file.filename)
        file.save(file_path)
        result = envoyer_emails(file_path)
        if result is True:
            flash("Les emails ont été envoyés avec succès !", "success")
        else:
            flash(f"Une erreur est survenue : {result}", "danger")
        return redirect(url_for('index'))

# -------------------------------------------------
# Endpoints de Tracking (duplicata conservé pour ne pas modifier la logique existante)
# -------------------------------------------------
@app.route('/tracking/open')
def tracking_open_endpoint():
    email = request.args.get('email')
    tracking_logger.info(f"Ouverture de mail par : {email}")
    transparent_path = os.path.join(script_directory, 'static', 'transparent.png')
    return send_file(transparent_path, mimetype='image/png')

@app.route('/click/<magasin>')
def click_tracking_endpoint(magasin):
    email = request.args.get('email')
    tracking_logger.info(f"Clic sur le lien pour {magasin} par : {email}")
    if magasin.lower() == 'nancy':
        url_finale = "https://g.page/r/Ccz4I1-xV-mxEBM/review"
    elif magasin.lower() == 'metz':
        url_finale = "https://g.page/r/CYNztFt83QRGEBM/review"
    elif magasin.lower() == 'strasbourg':
        url_finale = "https://g.page/r/CaMB1keRh-NgEBM/review"
    else:
        url_finale = "https://meubleprive.fr"
    return redirect(url_finale)

# -------------------------------------------------
# Lancement de l'application Flask
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
