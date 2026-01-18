
import pandas as pd
import streamlit as st
from LLM.runner import run_prompt

# ---------------- Page config ----------------
st.set_page_config(page_title="PromptLab", layout="wide")

# Minimal polish: hide Streamlit chrome + cap content width
st.markdown(
    """
    <style>
      #MainMenu {visibility: hidden;}
      header {visibility: hidden;}
      footer {visibility: hidden;}
      .block-container { max-width: 1100px; padding-top: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Title ----------------
st.title("🧪 PromptLab")
st.caption("Type multiple prompts, run them, and compare outputs.")

# ---------------- Sidebar controls ----------------
with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1"], index=0)
    max_tokens = st.slider("Max output tokens", 32, 2048, 256, 32)
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)

# ---------------- Session state ----------------
if "prompts" not in st.session_state:
    st.session_state.prompts = ["", ""]
if "results" not in st.session_state:
    st.session_state.results = []

# ---------------- Top action row ----------------
c1, c2, c3 = st.columns([1, 1, 2], vertical_alignment="center")

with c1:
    if st.button("➕ Add prompt"):
        st.session_state.prompts.append("")
        st.rerun()

with c2:
    run_clicked = st.button("▶️ Run", type="primary")

with c3:
    if st.button("🧹 New session"):
        st.session_state.prompts = ["", ""]
        st.session_state.results = []
        st.rerun()

st.divider()

# ---------------- Prompt inputs ----------------
st.subheader("Prompts")

for i in range(len(st.session_state.prompts)):
    left, right = st.columns([10, 2], vertical_alignment="center")

    with left:
        st.session_state.prompts[i] = st.text_area(
            label=f"Prompt {i+1}",
            value=st.session_state.prompts[i],
            height=100,
            key=f"prompt_{i}",
            placeholder="Write a complete prompt here...",
        )

    with right:
        disable_delete = len(st.session_state.prompts) <= 1
        if st.button(
            "🗑️ Delete",
            key=f"delete_{i}",
            disabled=disable_delete,
            use_container_width=True,
        ):
            st.session_state.prompts.pop(i)
            st.rerun()

# ---------------- Run logic ----------------
if run_clicked:
    cleaned_prompts = [p.strip() for p in st.session_state.prompts if p and p.strip()]
    if not cleaned_prompts:
        st.error("Add at least one non-empty prompt.")
        st.stop()

    rows = []
    for idx, prompt in enumerate(cleaned_prompts, start=1):
        try:
            result = run_prompt(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            rows.append(
                {
                    "#": idx,
                    "Prompt": prompt,
                    "Output": result.output_text,
                    "Latency (s)": round(result.latency_s, 3) if result.latency_s is not None else None,
                    "Tokens": result.total_tokens,
                    "Cost ($)": round(result.cost_usd, 6) if result.cost_usd is not None else None,
                }
            )
        except Exception as e:
            rows.append(
                {
                    "#": idx,
                    "Prompt": prompt,
                    "Output": f"ERROR: {e}",
                    "Latency (s)": None,
                    "Tokens": None,
                    "Cost ($)": None,
                }
            )

    st.session_state.results = rows
    st.rerun()

# ---------------- Results table ----------------
if st.session_state.results:
    st.subheader("Results")
    st.dataframe(
        pd.DataFrame(st.session_state.results),
        use_container_width=True,
        hide_index=True,
    )



