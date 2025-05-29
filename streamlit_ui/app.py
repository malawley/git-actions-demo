import streamlit as st
import requests
from google.cloud import storage
from datetime import datetime
import json
import os

# === Configuration ===
EXTRACTOR_URL = os.environ.get("EXTRACTOR_URL", "https://extractor-git-action-demo-931515156181.us-central1.run.app")
RAW_BUCKET = os.environ.get("RAW_BUCKET", "raw-inspection-data-434")
PREFIX = "git-action-demo"

st.set_page_config(page_title="Extractor UI", layout="centered")
st.title("Demo: GitHub Actions + Cloud Run: Extractor UI")

# === Health Check ===
st.header("🔍 Extractor Health Check")
try:
    r = requests.get(f"{EXTRACTOR_URL}/health", timeout=3)
    if r.status_code == 200:
        st.success("🟢 Extractor is alive")
    else:
        st.warning(f"⚠️ Extractor returned status: {r.status_code}")
except Exception as e:
    st.error(f"🔴 Could not reach extractor: {e}")

# === Extraction Form ===
st.header("📤 Extract Data from API")

with st.form("extract_form"):
    date = st.text_input("Date (YYYY-MM-DD)", value=str(datetime.today().date()))
    n_rows = st.number_input("Number of rows", value=500, min_value=1, step=100)
    submit = st.form_submit_button("▶️ Extract Now")

if submit:
    try:
        resp = requests.get(f"{EXTRACTOR_URL}/extract", params={"n": n_rows, "date": date})
        if resp.status_code == 200:
            st.success(f"✅ Extraction successful: {resp.json()}")
        else:
            st.error(f"❌ Extraction failed: {resp.status_code} – {resp.text}")
    except Exception as e:
        st.error(f"❌ Error triggering extractor: {e}")

# === GCS File Listing ===
st.header("📁 GCS Contents")

@st.cache_resource
def get_client():
    return storage.Client()

client = get_client()
prefix = f"{PREFIX}/{date}/"

try:
    bucket = client.bucket(RAW_BUCKET)
    blobs = list(bucket.list_blobs(prefix=prefix))
    st.write(f"**🧾 Files for {date}:** {len(blobs)} found")

    for blob in blobs:
        st.write(f"- `{blob.name}` ({blob.size:,} bytes)")
        with blob.open("r") as f:
            try:
                content = json.load(f)
                preview = json.dumps(content[:3], indent=2) if isinstance(content, list) else str(content)
                with st.expander("🔍 Preview JSON"):
                    st.code(preview, language="json")
            except Exception as e:
                st.error(f"⚠️ Could not parse JSON: {e}")

except Exception as e:
    st.error(f"❌ Failed to list files in GCS: {e}")
# trigger
# re-trigger
# re-trigger after secret fix
# re-run with fixed service account key
# re-trigger after Artifact Registry switch
# trigger for Artifact Registry
# next trigger for Artifact Registry
# trigger after fixing artifact registry permissions
# trigger for working deploy
