import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode  # Import the qrcode library
import io
import os

# --- Configuration ---
# Dimensions A4 en pixels (en supposant 300 DPI pour une bonne qualité d'impression)
A4_WIDTH_PX = 2480
A4_HEIGHT_PX = 3508

# Dimensions des étiquettes (70mm x 37mm converties en pixels à 300 DPI)
LABEL_WIDTH_PX = int((70 / 25.4) * 300)
LABEL_HEIGHT_PX = int((37 / 25.4) * 300)

# Marges/remplissage à l'intérieur d'une étiquette
LABEL_PADDING_X = 20
LABEL_PADDING_Y = 10

# Taille du QR Code (15mm x 15mm converties en pixels à 300 DPI)
QR_CODE_SIZE_PX = int((15 / 25.4) * 300)

# Chemins des polices
font_name = None
font_class_option = None
font_email = None
font_path = "Roboto-VariableFont_wdth,wght.ttf"

if os.path.exists(font_path):
    try:
        font_name = ImageFont.truetype(font_path, 50)
        font_class_option = ImageFont.truetype(font_path, 40)
        font_email = ImageFont.truetype(font_path, 40)
    except Exception as e:
        st.warning(f"Erreur lors du chargement de la police : {e}. Utilisation de la police par défaut.")
        font_name = ImageFont.load_default()
        font_class_option = ImageFont.load_default()
        font_email = ImageFont.load_default()
else:
    st.warning(
        "Police personnalisée 'Roboto-VariableFont_wdth,wght.ttf' non trouvée. Utilisation de la police par défaut. Pour de meilleurs résultats, placez le fichier de police dans le même répertoire que le script.")
    font_name = ImageFont.load_default()
    font_class_option = ImageFont.load_default()
    font_email = ImageFont.load_default()


# --- Fonctions ---
def generate_qr_code(data: str):
    """Génère une image de code QR à partir des données données."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((QR_CODE_SIZE_PX, QR_CODE_SIZE_PX))


def create_single_label_image(name: str, firstname: str, student_class: str, option: str, email: str):
    """
    Crée une image pour une seule étiquette avec toutes les données de l'élève et le code QR.
    """
    label_img = Image.new('RGB', (LABEL_WIDTH_PX, LABEL_HEIGHT_PX), color='white')
    draw = ImageDraw.Draw(label_img)

    # Calculer les positions du texte
    current_y = LABEL_PADDING_Y + 10

    # NOM PRENOM
    draw.text((LABEL_PADDING_X, current_y), f"{name}", fill=(0, 0, 0), font=font_name)
    current_y += font_name.getbbox(f"{name}")[3] - font_name.getbbox(f"{name}")[1] + 5

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
    if classe_option_lpeth_width > LABEL_WIDTH_PX - 2 * LABEL_PADDING_X:
        classe_option_lpeth_text = classe_option_lpeth_text[:int(
            (LABEL_WIDTH_PX - 2 * LABEL_PADDING_X) / (classe_option_lpeth_width / len(classe_option_lpeth_text)))] + "..."
    classe_option_lpeth_width = font_class_option.getbbox(classe_option_lpeth_text)[2] - font_class_option.getbbox(
        classe_option_lpeth_text)[0]

    draw.text((LABEL_PADDING_X, current_y), classe_option_lpeth_text, fill=(0, 0, 0), font=font_class_option)
    current_y += font_class_option.getbbox(classe_option_lpeth_text)[3] - font_class_option.getbbox(
        classe_option_lpeth_text)[1] + 15

    # QR Code
    qr_img = generate_qr_code(email)
    qr_x = (LABEL_WIDTH_PX - QR_CODE_SIZE_PX) // 2
    qr_y = LABEL_HEIGHT_PX - QR_CODE_SIZE_PX - LABEL_PADDING_Y
    label_img.paste(qr_img, (qr_x, qr_y))

    return label_img


def create_a4_sheet(labels_data: dict):
    """
    Crée une feuille A4 complète avec des étiquettes aux positions spécifiées.
    labels_data est un dictionnaire où les clés sont les positions des étiquettes et les valeurs sont les images d'étiquettes générées.
    """
    a4_sheet = Image.new('RGB', (A4_WIDTH_PX, A4_HEIGHT_PX), color='white')
    for (x, y), label_img in labels_data.items():
        a4_sheet.paste(label_img, (x, y))
    return a4_sheet


# --- Application Streamlit ---
st.set_page_config(page_title="Générateur d'Étiquettes LPETH", layout="centered")
st.title("🏷️ Générateur d'Étiquettes LPETH")

st.markdown("""
Bienvenue dans le générateur d'étiquettes pour les élèves du LPETH !
Remplissez les informations de l'élève ci-dessous et choisissez l'emplacement de l'étiquette sur la feuille A4.
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

    st.subheader("Emplacement de l'étiquette sur la feuille A4")
    # Créer une zone de sélection d'emplacement plus visuelle
    cols = st.columns(3)  # Diviser la largeur en 3 colonnes pour l'affichage de la grille
    label_positions = {}
    for row in range(8):  # 8 lignes d'étiquettes
        for col in range(3):  # 3 colonnes d'étiquettes
            position_number = row * 3 + col + 1
            with cols[col]:
                if st.button(f"Emplacement {position_number}", key=f"pos_{position_number}"): #ajouter une key
                    label_x = col * LABEL_WIDTH_PX
                    label_y = row * LABEL_HEIGHT_PX
                    label_positions[position_number] = (label_x, label_y)
                    st.session_state['selected_position'] = (label_x, label_y) #sauvegarde de la position choisie

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

        # Préparer les données pour la feuille A4.
        if 'selected_position' in st.session_state:
            labels_to_place = {st.session_state['selected_position']: single_label_img}
        else:
             labels_to_place = {(0,0): single_label_img} #Valeur par défaut

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
