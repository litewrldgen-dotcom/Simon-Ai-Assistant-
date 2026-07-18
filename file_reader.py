from PyPDF2 import PdfReader  # CHANGED THIS LINE
from PIL import Image
import base64
import io
import streamlit as st

def read_file(uploaded_file):
    """
    Reads PDF, TXT, IMG and returns text + base64 image for HF Vision
    """
    file_type = uploaded_file.type
    text_content = ""
    image_data = None

    # 1. IMAGE HANDLING - FOR QWEN2.5-VL VISION
    if "image" in file_type:
        img = Image.open(uploaded_file)
        st.image(img, caption="📸 Uploaded Image", width=250) # show preview
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        image_data = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        text_content = "User uploaded an image. Analyze it."

    # 2. PDF HANDLING - FIXED FOR STREAMLIT
    elif "pdf" in file_type:
        reader = PdfReader(uploaded_file)
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text())
        text_content = "\n".join(pages)
        st.success(f"📄 Read {len(reader.pages)} pages from PDF")

    # 3. TXT / CSV / DOCX HANDLING
    else:
        try:
            text_content = uploaded_file.read().decode("utf-8")
        except:
            text_content = "Could not read file"

    return text_content[:4000], image_data  # limit to 4000 chars for HF