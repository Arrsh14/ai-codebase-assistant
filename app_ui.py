import streamlit as st
from generate import ask

st.set_page_config(page_title="AI Codebase Assistant", page_icon="🧠")

st.title("🧠 AI Codebase Assistant")
st.write("Ask a question about your codebase and get a grounded answer with sources.")

question = st.text_input("Ask a question:")

if st.button("Ask") and question.strip():
    with st.spinner("Thinking..."):
        answer = ask(question)
    st.markdown("### Answer")
    st.write(answer)