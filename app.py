import streamlit as st
from gamma_service import create_presentation_from_text

# ---- Page setup ----
st.set_page_config(
    page_title="AI Presentation Generator",
    page_icon="🎨",
    layout="centered",
)

# ---- Header ----
st.title("🎨 AI Presentation Generator")
st.markdown(
    """
    Create brand-new **AI presentations** instantly from your input text.  
    Just enter your topic or paragraph — I am going to generate a presentation for you in (PDF or PPTX).
    """
)
st.divider()

# ---- Input Area ----
st.subheader("Generate a Presentation")
topic = st.text_input("Enter a topic or title:", "Top 5 Pizza Places in NYC")

content = st.text_area(
    "Add a short description or content:",
    "List and describe the top 5 pizza places in New York City with ratings, specialties, and unique features.",
    height=150,
)

export_as = st.selectbox("Export format", ["pdf", "pptx"])
num_cards = st.slider("Number of slides", 1, 10, 5)

# ---- Button ----
if st.button("🚀 Generate Presentation"):
    with st.spinner("Creating your presentation... please wait ⏳"):
        text_to_send = f"Title: {topic}\n\nContent:\n{content}"
        result = create_presentation_from_text(text_to_send, export_as, num_cards)

        if "error" in result:
            st.error(result["error"])
        else:
            st.success("✅ Presentation created successfully!")
            st.markdown(f"**Download link:** [{result['url']}]({result['url']})")

            # Provide Streamlit download button
            with open(result["file"], "rb") as f:
                st.download_button(
                    label=f"⬇️ Download {export_as.upper()} File",
                    data=f,
                    file_name=result["file"],
                    mime=(
                        "application/pdf"
                        if export_as == "pdf"
                        else "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    ),
                )

st.markdown("---")
st.caption("Built by fundae AI")
