import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode
import io
import os

# ---------------- CONFIGURATION ----------------
st.set_page_config(page_title="Générateur d'Étiquettes LPETH", layout="centered")

# Dimensions A4 à 300 DPI
A4_WIDTH_PX = 2480
A4_HEIGHT_PX = 3508

# Dimensions étiquette : 70mm x 37mm en pixels
LABEL_WIDTH_PX = int((70 / 25.4) * 300)
LABEL_HEIGHT_PX = int((37 / 25.4) * 300)

# Rembourrage intérieur
LABEL_PADDING_X = 20
LABEL_PADDING_Y = 10

# QR Code : 15mm x 15mm
QR_CODE_SIZE_PX = int((15 / 25.4) * 300)

# ---------------- POLICE ----------------
font_path = "assets/Roboto-Regular.ttf"
try:
    font_name = ImageFont.truetype(font_path, 50)
    font_class_option = ImageFont.truetype(font_path, 40)
    font_email = ImageFont.truetype(font_path, 40)
except IOError:
    st.warning("Impossible de charger la police personnalisée. Utilisation de la police par défaut.")
    font_name = ImageFont.load_default()
    font_class_option = ImageFont.load_default()
    font_email = ImageFont.load_default()

# ---------------- FONCTIONS ----------------
def generate_qr_code(data: str):
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


def create_single_label_image(name, firstname, student_class, option, email):
    label_img = Image.new('RGB', (LABEL_WIDTH_PX, LABEL_HEIGHT_PX), color='white')
    draw = ImageDraw.Draw(label_img)

    current_y = LABEL_PADDING_Y + 10

    draw.text((LABEL_PADDING_X, current_y), name, fill="black", font=font_name)
    current_y += font_name.getbbox(name)[3] - font_name.getbbox(name)[1] + 5

    draw.text((LABEL_PADDING_X, current_y), firstname, fill="black", font=font_name)
    current_y += font_name.getbbox(firstname)[3] - font_name.getbbox(firstname)[1] + 10

    draw.text((LABEL_PADDING_X, current_y), email, fill="black", font=font_email)
    current_y += font_email.getbbox(email)[3] - font_email.getbbox(email)[1] + 15

    ligne = f"{student_class}  |  {option}  |  LPETH"
    largeur = font_class_option.getbbox(ligne)[2] - font_class_option.getbbox(ligne)[0]
    if largeur > LABEL_WIDTH_PX - 2 * LABEL_PADDING_X:
        ligne = ligne[:int((LABEL_WIDTH_PX - 2 * LABEL_PADDING_X) / (largeur / len(ligne)))] + "..."
    draw.text((LABEL_PADDING_X, current_y), ligne, fill="black", font=font_class_option)

    # QR
    qr_img = generate_qr_code(email)
    qr_x = (LABEL_WIDTH_PX - QR_CODE_SIZE_PX) // 2
    qr_y = LABEL_HEIGHT_PX - QR_CODE_SIZE_PX - LABEL_PADDING_Y
    label_img.paste(qr_img, (qr_x, qr_y))

    return label_img


def create_a4_sheet(labels_data: dict):
    a4_sheet = Image.new('RGB', (A4_WIDTH_PX, A4_HEIGHT_PX), color='white')
    for position, label_img in labels_data.items():
        col = (position - 1) % 3
        row = (position - 1) // 3
        x_offset = col * LABEL_WIDTH_PX
        y_offset = row * LABEL_HEIGHT_PX
        a4_sheet.paste(label_img, (x_offset, y_offset))
    return a4_sheet


def display_position_grid(selected):
    st.markdown("### Grille de position (3 colonnes × 8 lignes)")
    cols = st.columns(3)
    for row in range(8):
        for col in range(3):
            pos = row * 3 + col + 1
            with cols[col]:
                st.markdown(
                    f"<div style='border:1px solid #ccc; padding:10px; "
                    f"margin:2px; text-align:center; font-weight:bold; "
                    f"background-color:{'#4CAF50' if pos == selected else '#f0f0f0'};'>"
                    f"{pos}</div>", unsafe_allow_html=True
                )

# ---------------- UI ----------------
st.title("🏷️ Générateur d'Étiquettes LPETH")

st.markdown("""
Bienvenue dans le générateur d'étiquettes pour les élèves du LPETH !  
Remplissez les informations ci-dessous et choisissez la position sur la feuille A4.
""")

with st.form("label_form"):
    st.subheader("Informations de l'élève")
    student_name = st.text_input("Nom de l'élève", help="Ex : DUPONT").upper()
    student_firstname = st.text_input("Prénom de l'élève", help="Ex : Jean").capitalize()
    student_class = st.text_input("Classe", help="Ex : 6TTI").upper()
    student_option = st.text_input("Option", help="Ex : Informatique")
    student_email_prefix = st.text_input("Préfixe Email (avant @eduhainaut.be)", help="Ex: jean.dupont")

    full_email = f"{student_email_prefix}@eduhainaut.be" if student_email_prefix else ""
    if full_email:
        st.info(f"Adresse email générée : **{full_email}**")

    st.subheader("Position de l'étiquette sur la feuille A4")
    selected_position = st.selectbox("Choisir la position de l'étiquette", list(range(1, 25)))
    display_position_grid(selected_position)

    submitted = st.form_submit_button("Générer l'étiquette")

if submitted:
    if not (student_name and student_firstname and student_class and student_email_prefix):
        st.error("Veuillez remplir toutes les informations requises.")
    else:
        st.success("✅ Étiquette générée avec succès !")

        label_img = create_single_label_image(
            student_name, student_firstname, student_class, student_option, full_email
        )

        a4_sheet = create_a4_sheet({selected_position: label_img})

        st.image(a4_sheet, caption="Aperçu de la feuille A4 avec étiquette", use_container_width=True)

        buf = io.BytesIO()
        a4_sheet.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="📥 Télécharger la feuille A4 (PNG)",
            data=byte_im,
            file_name="etiquette_LPETH.png",
            mime="image/png"
        )

st.markdown("---")
st.markdown("Développé avec ❤️ pour le LPETH")
