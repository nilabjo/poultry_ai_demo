import json
import requests
import streamlit as st

st.set_page_config(page_title="🐔 Poultry Symptom Checker", page_icon="🐔", layout="centered")
st.title("🐔 Poultry Symptom Checker")
st.caption("AI-powered diagnosis from your n8n workflow.")

WEBHOOK_URL = "https://YOURNAME.app.n8n.cloud/webhook/poultry-dx"  # <-- put your Production URL here

def safe_parse(resp: requests.Response):
    """Return a dict. Try JSON; if text looks like JSON inside, extract; else fallback."""
    try:
        return resp.json()
    except Exception:
        t = resp.text.strip()
        # try to extract JSON block if escaped/with newlines
        s, e = t.find("{"), t.rfind("}")
        if s != -1 and e != -1 and e > s:
            try:
                return json.loads(t[s:e+1])
            except Exception:
                pass
        return {"raw_text": t}

species = st.selectbox("Species", ["chicken", "duck", "turkey", "quail"], index=0)
age_weeks = st.number_input("Age (weeks)", min_value=0, value=10)
symptoms = st.text_area("Symptoms (comma-separated)", "coughing, watery diarrhea", height=100)

if st.button("Diagnose"):
    if not WEBHOOK_URL or "webhook" not in WEBHOOK_URL:
        st.error("Please set your n8n Production Webhook URL at the top of app.py.")
        st.stop()
    payload = {"species": species, "age_weeks": age_weeks, "symptoms": symptoms.strip()}
    with st.spinner("Contacting the AI workflow..."):
        try:
            r = requests.post(WEBHOOK_URL, json=payload, timeout=60)
            r.raise_for_status()
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    data = safe_parse(r)

    if "raw_text" in data:
        st.warning("The workflow returned unstructured text. Showing raw output below.")
        st.code(data["raw_text"])
        st.info("Tip: Ensure your n8n Code node parses JSON and Respond to Webhook returns {{$json}} as JSON.")
        st.stop()

    # Pretty, structured rendering
    st.success("✅ Diagnosis received")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Diagnosis")
        st.write(f"**{data.get('diagnosis','—')}**")
        st.write(f"_Confidence_: {data.get('confidence','—')}  ·  _Risk_: {data.get('risk_level','—')}")
    with col2:
        st.subheader("Immediate Steps")
        for step in (data.get("remedy", {}).get("immediate_steps", []) or []):
            st.write(f"- {step}")

    st.subheader("Treatment Plan")
    for step in (data.get("remedy", {}).get("treatment_plan", []) or []):
        st.write(f"- {step}")

    red = data.get("red_flags") or []
    if red:
        st.subheader("⚠️ Red Flags")
        for rf in red:
            st.write(f"- {rf}")

    refs = data.get("references") or []
    if refs:
        st.subheader("📚 References")
        for ref in refs:
            st.write(f"- {ref}")
