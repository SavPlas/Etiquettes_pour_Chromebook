    import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode  # Import the qrcode library
import io

# --- Configuration ---
# Dimensions A4 en pixels (en supposant 300 DPI pour une bonne qualité d'impression)
A4_WIDTH_PX = 2480
A4_HEIGHT_PX = 3508

# Dimensions des étiquettes (70mm x 37mm converties en pixels à 300 DPI)
LABEL_WIDTH_PX = int((70 / 25.4) * 300)  # 70mm à 300 DPI
LABEL_HEIGHT_PX = int((37 / 25.4) * 300)  # 37mm à 300 DPI

# Marges/remplissage à l'intérieur d'une étiquette
LABEL_PADDING_X = 20  # Réduit le rembourrage pour mieux adapter le contenu
LABEL_PADDING_Y = 10  # Réduit le rembourrage pour mieux adapter le contenu

# Taille du QR Code (15mm x 15mm converties en pixels à 300 DPI)
QR_CODE_SIZE_PX = int((15 / 25.4) * 300)  # 15mm à 300 DPI

# Chemins des polices
font_name = None
font_class_option = None
font_email = None
try:
    font_name = ImageFont.truetype("arial.ttf", 50)  # Augmente la taille de la police
    font_class_option = ImageFont.truetype("arial.ttf", 40)  # Augmente la taille de la police
    font_email = ImageFont.truetype("arial.ttf", 40)  # Augmente la taille de la police
except IOError:
    st.warning(
        "Impossible de charger 'arial.ttf'. Utilisation de la police par défaut. Pour de meilleurs résultats, fournissez un chemin vers un fichier .ttf.")
    font_name = ImageFont.load_default()
    font_class_option = ImageFont.load_default()
    font_email = ImageFont.load_default()


# --- Fonctions ---

def generate_qr_code(data: str):
    """Génère une image de code QR à partir des données données."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,  # Réduit la taille de la boîte pour un QR code plus petit
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((QR_CODE_SIZE_PX, QR_CODE_SIZE_PX))  # Redimensionne le QR code à la taille désirée


def create_single_label_image(name: str, firstname: str, student_class: str, option: str, email: str):
    """
    Crée une image pour une seule étiquette avec toutes les données de l'élève et le code QR.
    """
    label_img = Image.new('RGB', (LABEL_WIDTH_PX, LABEL_HEIGHT_PX), color='white')
    draw = ImageDraw.Draw(label_img)

    # Calculer les positions du texte
    current_y = LABEL_PADDING_Y + 10  # Déplace le texte vers le bas en augmentant la valeur initiale de current_y

    # NOM PRENOM
    draw.text((LABEL_PADDING_X, current_y), f"{name}", fill=(0, 0, 0), font=font_name)
    current_y += font_name.getbbox(f"{name}")[3] - font_name.getbbox(f"{name}")[1] + 5  # Réduit l'espacement

    # Prénom
    draw.text((LABEL_PADDING_X, current_y), f"{firstname}", fill=(0, 0, 0), font=font_name)
    current_y += font_name.getbbox(f"{firstname}")[3] - font_name.getbbox(f"{firstname}")[1] + 10

    # Email
    draw.text((LABEL_PADDING_X, current_y), f"{email}", fill=(0, 0, 0), font=font_email)
    current_y += font_email.getbbox(f"{email}")[3] - font_email.getbbox(f"{email}")[1] + 15

    # CLASSE, OPTION, LPETH sur la même ligne
    classe_option_lpeth_text = f"{student_class}  |  {option}  |  LPETH"
    classe_option_lpeth_width = font_class_option.getbbox(classe_option_lpeth_text)[2] - font_class_option.getbbox(
        classe_option_lpeth_text)[0]
    # Si le texte est trop long, le tronquer
    if classe_option_lpeth_width > LABEL_WIDTH_PX - 2 * LABEL_PADDING_X:
        classe_option_lpeth_text = classe_option_lpeth_text[:int(
            (LABEL_WIDTH_PX - 2 * LABEL_PADDING_X) / (classe_option_lpeth_width / len(classe_option_lpeth_text)))] + "..."
    classe_option_lpeth_width = font_class_option.getbbox(classe_option_lpeth_text)[2] - font_class_option.getbbox(
        classe_option_lpeth_text)[0]

    draw.text((LABEL_PADDING_X, current_y), classe_option_lpeth_text, fill=(0, 0, 0), font=font_class_option)
    current_y += font_class_option.getbbox(classe_option_lpeth_text)[3] - font_class_option.getbbox(
        classe_option_lpeth_text)[1] + 15  # Augmente l'espacement

    # QR Code
    qr_img = generate_qr_code(email)
    # Centrer le QR code et le placer plus bas
    qr_x = (LABEL_WIDTH_PX - QR_CODE_SIZE_PX) // 2
    qr_y = LABEL_HEIGHT_PX - QR_CODE_SIZE_PX - LABEL_PADDING_Y  # Place le QR code en bas
    label_img.paste(qr_img, (qr_x, qr_y))

    return label_img


def create_a4_sheet(labels_data: dict):
    """
    Crée une feuille A4 complète avec des étiquettes aux positions spécifiées.
    labels_data est un dictionnaire où les clés sont les positions des étiquettes (1-24) et les valeurs sont les images d'étiquettes générées.
    """
    a4_sheet = Image.new('RGB', (A4_WIDTH_PX, A4_HEIGHT_PX), color='white')

    for position, label_img in labels_data.items():
        # Calculer la ligne et la colonne à partir de la position (1-24)
        col = (position - 1) % 3
        row = (position - 1) // 3

        x_offset = col * LABEL_WIDTH_PX
        y_offset = row * LABEL_HEIGHT_PX

        a4_sheet.paste(label_img, (x_offset, y_offset))

    return a4_sheet


# --- Application Streamlit ---
st.set_page_config(page_title="Générateur d'Étiquettes LPETH", layout="centered")

st.title("🏷️ Générateur d'Étiquettes LPETH")

st.markdown("""
Bienvenue dans le générateur d'étiquettes pour les élèves du LPETH !
Remplissez les informations de l'élève ci-dessous et choisissez la position de l'étiquette sur la feuille A4.
""")

with st.form("label_form"):
    st.subheader("Informations de l'élève")
    student_name = st.text_input("Nom de l'élève", help="Ex : DUPONT").upper()
    student_firstname = st.text_input("Prénom de l'élève", help="Ex : Jean").capitalize()
    student_class = st.text_input("Classe", help="Ex : 6TTI").upper()
    student_option = st.text_input("Option", help="Ex : Informatique")
    student_email_prefix = st.text_input("Préfixe Email (avant @eduhainaut.be)", help="Ex: jean.dupont")

    full_email = f"{student_email_prefix}@eduhainaut.be" if student_email_prefix else ""
    st.info(f"L'adresse email générée sera : **{full_email}**")

    st.subheader("Position de l'étiquette sur la feuille A4")
    label_positions = list(range(1, 25))
    selected_position = st.selectbox("Choisir la position de l'étiquette", label_positions)

    submitted = st.form_submit_button("Générer l'étiquette")

if submitted:
    if not (student_name and student_firstname and student_class and student_email_prefix):
        st.error("Veuillez remplir toutes les informations requises (Nom, Prénom, Classe, Préfixe Email).")
    else:
        st.success("Étiquette générée avec succès ! 👇")

        # Créer l'image de l'étiquette unique
        single_label_img = create_single_label_image(
            student_name,
            student_firstname,
            student_class,
            student_option,
            full_email
        )

        # Préparer les données pour la feuille A4. Nous n'avons qu'une seule étiquette à placer pour l'instant.
        labels_to_place = {selected_position: single_label_img}

        # Créer la feuille A4 complète
        final_a4_sheet = create_a4_sheet(labels_to_place)

        st.image(final_a4_sheet, caption="Aperçu de la feuille d'étiquettes", use_container_width=True)

        # Fournir un bouton de téléchargement
        buf = io.BytesIO()
        final_a4_sheet.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="Télécharger la feuille d'étiquettes (PNG)",
            data=byte_im,
            file_name="feuille_etiquettes_LPETH.png",
            mime="image/png"
        )

        st.info("Pour imprimer, téléchargez l'image et imprimez-la sur une feuille A4 pour étiquettes.")

st.markdown("---")
st.markdown("Développé avec ❤️ pour le LPETH")
