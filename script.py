import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode
import io
import os

# --- Configuration ---
A4_WIDTH_PX = 2480
A4_HEIGHT_PX = 3508

LABEL_WIDTH_PX = int((70 / 25.4) * 300)  # 70 mm en pixels
LABEL_HEIGHT_PX = int((36 / 25.4) * 300)  # 36 mm en pixels (modifié)

LABEL_PADDING_X = 20
LABEL_PADDING_Y = 10

QR_CODE_SIZE_PX = int((15 / 25.4) * 300)

# Marges et espacement entre étiquettes
MARGIN_LEFT = int((5 / 25.4) * 300)   # 5 mm marge à gauche
MARGIN_TOP = int((5 / 25.4) * 300)    # 5 mm marge en haut

SPACING_X = 10  # espace horizontal entre étiquettes (en px)
SPACING_Y = 5   # espace vertical entre étiquettes (en px)

font_path = "Roboto-VariableFont_wdth,wght.ttf"
if os.path.exists(font_path):
    try:
        font_name = ImageFont.truetype(font_path, 50)
        font_class_option = ImageFont.truetype(font_path, 40)
        font_email = ImageFont.truetype(font_path, 40)
    except Exception as e:
        st.warning(f"Erreur chargement police : {e}. Police par défaut utilisée.")
        font_name = ImageFont.load_default()
        font_class_option = ImageFont.load_default()
        font_email = ImageFont.load_default()
else:
    st.warning("Police personnalisée non trouvée, police par défaut utilisée.")
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

def create_single_label_image(name, firstname, student_class, option, email):
    label_img = Image.new('RGB', (LABEL_WIDTH_PX, LABEL_HEIGHT_PX), color='white')
    draw = ImageDraw.Draw(label_img)
    current_y = LABEL_PADDING_Y + 10

    draw.text((LABEL_PADDING_X, current_y), name, fill=(0, 0, 0), font=font_name)
    bbox = font_name.getbbox(name)
    current_y += bbox[3] - bbox[1] + 5

    draw.text((LABEL_PADDING_X, current_y), firstname, fill=(0, 0, 0), font=font_name)
    bbox = font_name.getbbox(firstname)
    current_y += bbox[3] - bbox[1] + 10

    draw.text((LABEL_PADDING_X, current_y), email, fill=(0, 0, 0), font=font_email)
    bbox = font_email.getbbox(email)
    current_y += bbox[3] - bbox[1] + 15

    text_line = f"{student_class}  |  {option}  |  LPETH"
    max_width = LABEL_WIDTH_PX - 2 * LABEL_PADDING_X
    bbox = font_class_option.getbbox(text_line)
    text_width = bbox[2] - bbox[0]
    if text_width > max_width:
        max_chars = int(len(text_line) * max_width / text_width) - 3
        text_line = text_line[:max_chars] + "..."
        bbox = font_class_option.getbbox(text_line)

    draw.text((LABEL_PADDING_X, current_y), text_line, fill=(0, 0, 0), font=font_class_option)
    current_y += bbox[3] - bbox[1] + 15

    qr_img = generate_qr_code(email)
    qr_x = (LABEL_WIDTH_PX - QR_CODE_SIZE_PX) // 2
    qr_y = LABEL_HEIGHT_PX - QR_CODE_SIZE_PX - LABEL_PADDING_Y - 20
    label_img.paste(qr_img, (qr_x, qr_y))

    return label_img

def create_a4_sheet(labels_data):
    a4_sheet = Image.new('RGB', (A4_WIDTH_PX, A4_HEIGHT_PX), color='white')

    for position, label_img in labels_data.items():
        col = (position - 1) % 3
        row = (position - 1) // 3

        x_offset = MARGIN_LEFT + col * (LABEL_WIDTH_PX + SPACING_X)
        y_offset = MARGIN_TOP + row * (LABEL_HEIGHT_PX + SPACING_Y)

        a4_sheet.paste(label_img, (x_offset, y_offset))

    return a4_sheet

def create_position_grid(selected_pos):
    grid_img = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
    draw = ImageDraw.Draw(grid_img)

    for pos in range(1, 25):
        col = (pos - 1) % 3
        row = (pos - 1) // 3
        x = MARGIN_LEFT + col * (LABEL_WIDTH_PX + SPACING_X)
        y = MARGIN_TOP + row * (LABEL_HEIGHT_PX + SPACING_Y)
        box_color = (255, 255, 255)
        outline_color = (0, 0, 0)

        if pos == selected_pos:
            outline_color = (255, 0, 0)
            box_color = (255, 230, 230)

        draw.rectangle([x, y, x + LABEL_WIDTH_PX, y + LABEL_HEIGHT_PX], fill=box_color, outline=outline_color, width=5)
        text = str(pos)
        bbox = font_name.getbbox(text)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        text_x = x + (LABEL_WIDTH_PX - w) // 2
        text_y = y + (LABEL_HEIGHT_PX - h) // 2
        draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font_name)

    return grid_img

# --- Application Streamlit ---
st.set_page_config(page_title="Générateur d'Étiquettes LPETH pour les boîtes de Chromebook", layout="centered")
st.title("Générateur d'Étiquettes LPETH")

st.markdown("""
Bienvenue dans le générateur d'étiquettes pour les élèves du LPETH !
Remplissez les informations ci-dessous et cliquez sur la position de l'étiquette à imprimer.
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

    submitted = st.form_submit_button("Passer à la sélection de position")

if submitted:
    if not (student_name and student_firstname and student_class and student_email_prefix):
        st.error("Veuillez remplir toutes les informations requises (Nom, Prénom, Classe, Préfixe Email).")
    else:
        st.session_state["student_data"] = {
            "name": student_name,
            "firstname": student_firstname,
            "class": student_class,
            "option": student_option,
            "email": full_email
        }

# --- Grille de positions ---
if "student_data" in st.session_state:
    st.subheader("Choisissez la position de l'étiquette sur la feuille A4")
    if "selected_position" not in st.session_state:
        st.session_state.selected_position = None

    for row in range(8):
        cols = st.columns(3)
        for col in range(3):
            pos = row * 3 + col + 1
            if cols[col].button(f"{pos}"):
                st.session_state.selected_position = pos

    selected_position = st.session_state.selected_position
    if selected_position:
        st.success(f"Position sélectionnée : {selected_position}")

        data = st.session_state["student_data"]
        single_label_img = create_single_label_image(
            data["name"], data["firstname"], data["class"], data["option"], data["email"]
        )
        labels_to_place = {selected_position: single_label_img}
        final_a4_sheet = create_a4_sheet(labels_to_place)

        st.image(final_a4_sheet, caption="Aperçu de la feuille d'étiquettes", use_container_width=True)

        buf = io.BytesIO()
        final_a4_sheet.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="Télécharger la feuille d'étiquettes (PNG)",
            data=byte_im,
            file_name="feuille_etiquettes_LPETH.png",
            mime="image/png"
        )

        grid_img = create_position_grid(selected_position)
        st.markdown("### Grille des positions d'étiquette (position sélectionnée en rouge)")
        st.image(grid_img, use_container_width=True)

st.markdown("---")
st.markdown("Développé avec ❤️ pour le LPETH")
