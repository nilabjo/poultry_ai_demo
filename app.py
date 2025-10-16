import streamlit as st
import requests

st.set_page_config(page_title="🐔 Poultry Symptom Checker", page_icon="🐔", layout="centered")
st.title("🐔 Poultry Symptom Checker")
st.caption("AI-powered diagnosis from your n8n workflow.")

WEBHOOK_URL = "https://pin261987.app.n8n.cloud/webhook/poultry-dx"  # 👈 replace with your n8n Production URL

species = st.selectbox("Species", ["chicken", "duck", "turkey", "quail"], index=0)
age_weeks = st.number_input("Age (weeks)", min_value=0, value=10)
symptoms = st.text_area("Symptoms", "coughing, watery diarrhea", height=100)

if st.button("Diagnose"):
    with st.spinner("Contacting the AI workflow..."):
        payload = {
            "species": species,
            "age_weeks": age_weeks,
            "symptoms": symptoms.strip()
        }
        try:
            res = requests.post(WEBHOOK_URL, json=payload, timeout=60)
            res.raise_for_status()
            data = res.json()

            if "diagnosis" in data:
                st.success("✅ Diagnosis Complete")
                st.write(f"**Diagnosis:** {data.get('diagnosis','—')}")
                st.write(f"**Confidence:** {data.get('confidence','—')}")
                st.write(f"**Risk Level:** {data.get('risk_level','—')}")
                st.subheader("Immediate Steps")
                for s in data.get("remedy", {}).get("immediate_steps", []):
                    st.write(f"- {s}")
                st.subheader("Treatment Plan")
                for s in data.get("remedy", {}).get("treatment_plan", []):
                    st.write(f"- {s}")
                if data.get("red_flags"):
                    st.subheader("⚠️ Red Flags")
                    for r in data["red_flags"]:
                        st.write(f"- {r}")
                if data.get("references"):
                    st.subheader("📚 References")
                    for r in data["references"]:
                        st.write(f"- {r}")
            else:
                st.warning("Unexpected response:")
                st.code(res.text)
        except Exception as e:
            st.error(f"Error: {e}")
