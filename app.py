import streamlit as st

# ---- Page setup ----
st.set_page_config(
    page_title="Gamma AI Presentation Viewer",
    page_icon="🎨",
    layout="wide",
)

# ---- Header ----
st.title("🎨 Gamma AI Presentation Demo")
st.markdown(
    """
    This demo showcases how Gamma presentations can be viewed directly inside our platform.
    You can paste one or more **Gamma deck URLs** below to preview them live.
    """
)

st.divider()

# ---- Instructions ----
st.subheader("📋 Paste your Gamma presentation links")
st.caption("Example: https://gamma.app/docs/ai-trends-2025 or https://gamma.app/presentations/xyz123")

# ---- Input area ----
links_input = st.text_area(
    "Enter one or more Gamma presentation URLs (one per line):",
    placeholder="https://gamma.app/docs/ai-trends-2025\nhttps://gamma.app/docs/marketing-deck-demo",
    height=150,
)

# ---- Display area ----
if st.button("▶️ Show Presentations"):
    links = [link.strip() for link in links_input.splitlines() if link.strip()]
    if not links:
        st.warning("Please enter at least one valid Gamma presentation link.")
    else:
        for i, link in enumerate(links, start=1):
            st.markdown(f"### 📑 Presentation {i}")
            st.markdown(f"[Open in Gamma]({link})")
            # Embedded iframe preview
            st.components.v1.iframe(src=link, height=650, scrolling=True)
            st.divider()
else:
    st.info("⬆️ Paste your Gamma deck links above and click **Show Presentations** to view them here.")

# ---- Footer ----
st.markdown("---")
st.caption("Powered by Gamma • Streamlit Demo for internal presentation preview • Fundae AI")
