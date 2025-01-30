import streamlit as st
from huggingface_hub import InferenceClient
p="C:\\Users\\alano\\code\\ADC2324D-2816-442C-A4E0-62A070BF620C (1).png"

st.image(p,width=300)



st.title("Welcome to AI Health Assistant")

st.write("Use the navigation on the left to interact with the system.")
st.write("Options available:")
st.write("- Medical Record: Manage patient records.")
st.write("- Ask Saleem: Chat with AI to analyze symptoms and get recommendations.")

st.sidebar.success("Select a page from the sidebar.")
