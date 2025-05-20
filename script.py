import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode
import io
import os

# --- Configuration ---
A4_WIDTH_PX = 2480
A4_HEIGHT_PX = 3508

LABEL_WIDTH_PX = int((70 / 25.4) * 300)  # 70mm à 300 DPI
LABEL_HEIGHT_PX = int((37 / 25.4) * 300)  # 37mm à 300 DPI

LABEL_PADDING_X = 20
LABEL_PADDING_Y = 10

QR_CODE_SIZE_PX = int((15 / 25.4) * 300)  # 15mm à 300 DPI

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
        "Police personnalisée 'Roboto-VariableFont_wdth,wght.ttf' non trouvée. Utilisation de la police par défaut. "
        "Pour de meilleurs résultats, placez le fichier de police dans le même répertoire que le script."
    )
    font_name = ImageFont.load_default()
    font_class_option = ImageFont.load_default()
    font_email = ImageFont.load_default()


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


def create_single_label_image(name: str, firstname: str, student_class: str, option: str, email: str):
    label_img = Image.new('RGB', (LABEL_WIDTH_PX, LABEL_HEIGHT_PX), color='white')
    draw = ImageDraw.Draw(label_img)

    current_y = LABEL_PADDING_Y + 10

    draw.text((LABEL_PADDING_X, current_y), f"{name}", fill=(0, 0, 0), font=font_name)
    current_y += font_name.getbbox(f"{name}")[3] - font_name.getbbox(f"{name}")[1] + 5

    draw.text((LABEL_PADDING_X, current_y), f"{firstname}", fill=(0, 0, 0), font=font_name)
    current_y += font_name.getbbox(f"{firstname}")[3] - font_name.getbbox(f"{firstname}")[1] + 10

    draw.text((LABEL_PADDING_X, current_y), f"{email}", fill=(0, 0, 0), font=font_email)
    current_y += font_email.getbbox(f"{email}")[3] - font_email.getbbox(f"{email}")[1] + 15

    classe_option_lpeth_text = f"{student_class}  |  {option}  |  LPETH"
    classe_option_lpeth_width = font_class_option.getbbox(classe_option_lpeth_text)[2] - font_class_option.getbbox(classe_option_lpeth_text)[0]

    if classe_option_lpeth_width > LABEL_WIDTH_PX - 2 * LABEL_PADDING_X:
        max_chars = int((LABEL_WIDTH_PX - 2 * LABEL_PADDING_X) / (classe_option_lpeth_width / len(classe_option_lpeth_text)))
        classe_option_lpeth_text = classe_option_lpeth_text[:max_chars] + "..."

    draw.text((LABEL_PADDING_X, current_y), classe_option_lpeth_text, fill=(0, 0, 0), font=font_class_option)
    current_y += font_class_option.getbbox(classe_option_lpeth_text)[3] - font_class_option.getbbox(classe_option_lpeth_text)[1] + 15

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


def create_position_grid(selected_position):
    grid_img = Image.new('RGB', (A4_WIDTH_PX, A4_HEIGHT_PX), color='white')
    draw = ImageDraw.Draw(grid_img)

    font = font_name  # Utiliser la même police

    for pos in range(1, 25):
        col = (pos - 1) % 3
        row = (pos - 1) // 3

        x = col * LABEL_WIDTH_PX
        y = row * LABEL_HEIGHT_PX

        # Rectangle de la position
        rect_color = (255, 0, 0) if pos == selected_position else (200, 200, 200)
        draw.rectangle([x, y, x + LABEL_WIDTH_PX, y + LABEL_HEIGHT_PX], outline=rect_color, width=5)

        # Numéro de position au centre
        text = str(pos)
        w, h = draw.textsize(text, font=font)
        text_x = x + (LABEL_WIDTH_PX - w) // 2
        text_y = y + (LABEL_HEIGHT_PX - h) // 2
        draw.text((text_x, text_y), text, fill=rect_color, font=font)

    return grid_img


# --- Application Streamlit ---
st.set_page_config(page_title="Générateur d'Étiquettes LPETH", layout="centered")

st.title("🏷️ Générateur d'Étiquettes LPETH")

st.markdown("""
Bienvenue dans le générateur d'étiquettes pour les élèves du LPETH !
Remplissez les informations de l'élève ci-dessous et choisissez la position de l'étiquette sur la feuille A4.
""")

with st.form("label_form"):
    st.subheader("Informations de l'élève")
    student_name = st.text_input("Nom de l'élève", help="Ex : DUPONT").upper()
    student_firstname = st.text_input("Prénom de l'élève", help="Ex : Jean").capitalize()
    student_class = st.text_input("Classe", help="Ex : 6TTI").upper()
    student_option = st.text_input("Option", help="Ex : Informatique")
    student_email_prefix = st.text_input("Préfixe Email (avant @eduhainaut.be)", help="Ex: jean.dupont")

    full_email = f"{student_email_prefix}@eduhainaut.be" if student_email_prefix else ""
    st.info(f"L'adresse email générée sera : **{full_email}**")

    st.subheader("Position de l'étiquette sur la feuille A4")
    label_positions = list(range(1, 25))
    selected_position = st.selectbox("Choisir la position de l'étiquette", label_positions)

    submitted = st.form_submit_button("Générer l'étiquette")

if submitted:
    if not (student_name and student_firstname and student_class and student_email_prefix):
        st.error("Veuillez remplir toutes les informations requises (Nom, Prénom, Classe, Préfixe Email).")
    else:
        st.success("Étiquette générée avec succès ! 👇")

        single_label_img = create_single_label_image(
            student_name,
            student_firstname,
            student_class,
            student_option,
            full_email
        )

        labels_to_place = {selected_position: single_label_img}

        final_a4_sheet = create_a4_sheet(labels_to_place)

        _ = st.image(final_a4_sheet, caption="Aperçu de la feuille d'étiquettes", use_container_width=True)

        buf = io.BytesIO()
        final_a4_sheet.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="Télécharger la feuille d'étiquettes (PNG)",
            data=byte_im,
            file_name="feuille_etiquettes_LPETH.png",
            mime="image/png"
        )

        _ = st.info("Téléchargez puis imprimez sur feuille A4 pour étiquettes.")

        grid_img = create_position_grid(selected_position)
        st.markdown("### Grille des positions d'étiquette (position sélectionnée en rouge)")
        _ = st.image(grid_img, use_container_width=True)

st.markdown("---")
st.markdown("Développé avec ❤️ pour le LPETH")
