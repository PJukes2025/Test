import streamlit as st
from datetime import datetime
import uuid
import json

# -------- Page setup --------
st.set_page_config(page_title="Session-State Tester", page_icon="🧪", layout="centered")

st.title("🧪 Streamlit Session-State Tester")
st.caption("Use this to confirm that `st.session_state`—especially `user_corrections`—persists across reruns in your environment.")

# -------- Hard init (do this FIRST) --------
if 'session_uid' not in st.session_state:
    st.session_state['session_uid'] = str(uuid.uuid4())

if 'counter' not in st.session_state:
    st.session_state['counter'] = 0

if 'user_corrections' not in st.session_state:
    st.session_state['user_corrections'] = {}

# -------- Helper(s) --------
def add_history(image_key: str, original: str, corrected: str):
    entry = {
        'timestamp': datetime.now().isoformat(),
        'image': image_key,
        'original': original or "",
        'corrected': corrected or "",
        'pattern_type': 'user_correction'
    }
    hk = f"{image_key}::history"
    st.session_state['user_corrections'].setdefault(hk, []).append(entry)

def save_override(image_key: str, original: str, corrected: str):
    """Create/update a per-image override (like the OCR app)."""
    add_history(image_key, original, corrected)
    if corrected and corrected.strip():
        st.session_state['user_corrections'][image_key] = {
            'original': original or "",
            'corrected': corrected,
            'timestamp': datetime.now().isoformat()
        }

def override_keys():
    return sorted([
        k for k, v in st.session_state['user_corrections'].items()
        if isinstance(v, dict) and 'corrected' in v and not k.endswith("::history")
    ])

# -------- Sidebar: quick actions --------
st.sidebar.header("Quick Actions")

if st.sidebar.button("➕ Increment counter"):
    st.session_state['counter'] += 1
    st.rerun()

c1, c2 = st.sidebar.columns(2)
if c1.button("🧪 Add dummy override"):
    save_override("TEST_KEY__DEMO", "orig text", "corrected text")
    st.rerun()
if c2.button("🧹 Clear ALL corrections"):
    st.session_state['user_corrections'] = {}
    st.rerun()

if st.sidebar.button("🔄 Force rerun now"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("**Session info**")
st.sidebar.write("Session UID:", st.session_state['session_uid'])
st.sidebar.write("Counter value:", st.session_state['counter'])
st.sidebar.write("Overrides count:", len(override_keys()))

# -------- Main: interactive save form (simulates your correction saver) --------
st.subheader("Save a Correction (simulated)")
with st.form("save_form", clear_on_submit=False):
    colk, _ = st.columns([2, 1])
    with colk:
        image_key = st.text_input("Image storage key", value="MY_IMAGE__123abc")
    original = st.text_area("Original text (can be empty)", height=80, value="")
    corrected = st.text_area("Corrected text (non-empty to create override)", height=120, value="")
    submitted = st.form_submit_button("Save Correction")
    if submitted:
        save_override(image_key, original, corrected)
        st.success("Saved to st.session_state['user_corrections'].")
        st.rerun()

# -------- Main: view & manage overrides --------
st.subheader("Current Overrides")
keys = override_keys()
if not keys:
    st.info("No overrides yet. Use the form above or 'Add dummy override' in the sidebar.")
else:
    chosen = st.selectbox("Select override to view/edit:", keys, index=0, key="chosen_key")
    current = st.session_state['user_corrections'].get(chosen, {})
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Stored Original**")
        st.code(current.get("original", "(unknown)") or "(unknown)")
    with c2:
        st.markdown("**Stored Corrected**")
        new_corr = st.text_area("Edit corrected text & Update", value=current.get("corrected", ""), height=120, key="edit_corr")

    b1, b2, b3 = st.columns(3)
    if b1.button("Update Override"):
        save_override(chosen, current.get("original", ""), new_corr)
        st.success("Override updated.")
        st.rerun()
    if b2.button("Delete Override"):
        if chosen in st.session_state['user_corrections']:
            del st.session_state['user_corrections'][chosen]
        st.success("Override deleted (history kept).")
        st.rerun()
    if b3.button("Delete Override + History"):
        if chosen in st.session_state['user_corrections']:
            del st.session_state['user_corrections'][chosen]
        hk = f"{chosen}::history"
        if hk in st.session_state['user_corrections']:
            del st.session_state['user_corrections'][hk]
        st.success("Override and history deleted.")
        st.rerun()

    st.markdown("**History for this key**")
    hk = f"{chosen}::history"
    hist = st.session_state['user_corrections'].get(hk, [])
    if not hist:
        st.caption("(No history yet.)")
    else:
        for i, h in enumerate(hist[::-1], start=1):
            st.write(f"**{i}.** {h.get('timestamp','')} — corrected →")
            st.code(h.get('corrected','') or "(empty)")

# -------- Raw debug view --------
st.subheader("Raw `user_corrections` (debug)")
st.json(st.session_state['user_corrections'])

st.caption("Tip: If this page never shows your saved data after clicks, the session may be restarting each run or cookies are blocked. Try a single tab, disable strict privacy mode, or another browser.")
