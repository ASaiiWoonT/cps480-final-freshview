"""Day 1 upload and preview skeleton; no model inference on startup."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from src.config import load_config
from src.images import read_image

st.set_page_config(page_title="FreshView", page_icon="🍌", layout="wide")
st.title("FreshView")
st.subheader("See your produce from every side")
st.write("Upload one to three photos of the same fruit or vegetable to preview your views.")
st.info("Day 1 preview: condition assessment will be available after model training and integration.")

config = load_config()
maximum = config["multiview"]["maximum_views"]
uploads = st.file_uploader(
    "Choose photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True,
    help="JPEG or PNG, up to 10 MB and 20 megapixels per photo.",
)
if len(uploads) > maximum:
    st.error(f"Choose at most {maximum} photos of the same item. Remove the extra files to continue.")
elif uploads:
    columns = st.columns(len(uploads))
    for number, (column, upload) in enumerate(zip(columns, uploads), start=1):
        with column:
            try:
                image = read_image(upload)
                st.image(image, caption=f"View {number}: {upload.name}", width="stretch")
            except ValueError as error:
                st.error(f"{upload.name}: {error}")
else:
    st.caption("Start with a clear photo, then add other sides of the same item.")

st.button("Assess visible condition", disabled=True)
st.divider()
st.caption("FreshView assesses visible produce condition. It cannot determine food safety or exact shelf life.")
