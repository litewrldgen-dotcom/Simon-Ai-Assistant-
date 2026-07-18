from pypdf import PdfReader
from PIL import Image
import base64, io, streamlit as st
def read_file(uploaded_file):
    if "image" in uploaded_file.type:
        img = Image.open(uploaded_file)
        st.image(img, width=200)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return "", "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    elif "pdf" in uploaded_file.type:
        reader = PdfReader(uploaded_file)
        text = "".join([p.extract_text() for p in reader.pages])
        return text, None
    return uploaded_file.read().decode(), None