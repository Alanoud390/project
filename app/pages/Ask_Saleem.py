import streamlit as st
import pandas as pd
from fuzzywuzzy import process
from huggingface_hub import InferenceClient
provider="together",
# API Key for Hugging Face
# API_KEY = "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"
API_KEY = "AIzaSyB0_LZvncvhyxqrIo8qU3zFDEJ6iTuiM0E"
MODEL_NAME = "deepseek-ai/DeepSeek-V3"  # Free, human-like conversation model
client = InferenceClient(api_key=API_KEY)

import google.generativeai as genai

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# File paths
patient_file = "patients_data.xlsx"
disease_file = "static/DiseaseAndSymptoms.csv"

# Load patient records
if patient_file:
    patient_df = pd.read_excel(patient_file)
else:
    patient_df = pd.DataFrame(columns=["Name", "Age", "Gender", "Medical History", "Current Medications"])

# Load disease and symptoms dataset
disease_df = pd.read_csv(disease_file)
disease_df.fillna("", inplace=True)

# Extract all unique symptoms from the dataset
all_symptoms = set()
for col in disease_df.columns[1:]:  # Skip the 'Disease' column
    all_symptoms.update(disease_df[col].dropna().str.strip().str.lower())

all_symptoms = sorted(list(all_symptoms))  # Sort for better user experience

# Create a mapping of symptoms to diseases
disease_df["All_Symptoms"] = disease_df.iloc[:, 1:].apply(lambda row: [symptom.strip().lower() for symptom in row if symptom], axis=1)
symptom_disease_mapping = {}
for _, row in disease_df.iterrows():
    for symptom in row["All_Symptoms"]:
        if symptom not in symptom_disease_mapping:
            symptom_disease_mapping[symptom] = set()
        symptom_disease_mapping[symptom].add(row["Disease"])

# Convert sets to lists
for symptom in symptom_disease_mapping:
    symptom_disease_mapping[symptom] = list(symptom_disease_mapping[symptom])

# Function to match symptoms using fuzzy matching
def correct_symptoms(user_input_symptoms):
    corrected_symptoms = []
    for symptom in user_input_symptoms:
        match, score = process.extractOne(symptom, all_symptoms)  # Get best match
        if score > 75:  # Accept match if confidence score is high enough
            corrected_symptoms.append(match)
    return corrected_symptoms

# Function to get possible diseases based on symptoms
def get_possible_diseases(symptoms):
    matched_diseases = set()
    for symptom in symptoms:
        if symptom in symptom_disease_mapping:
            matched_diseases.update(symptom_disease_mapping[symptom])
    return list(matched_diseases)

# Function to get patient medical record
def get_patient_record(name):
    record = patient_df[patient_df["Name"].str.lower() == name.lower()]
    if not record.empty:
        return record.iloc[0].to_dict()
    return None

# Function to get AI-generated conversation-like response
def get_saleem_response(user_input, symptoms, medical_history, medications):
    prompt = (
        f"You are Saleem, a friendly and knowledgeable AI health assistant. Your goal is to provide helpful and conversational responses. "
        f"Avoid direct medical diagnoses but suggest practical actions to improve the user's well-being.\n\n"
        f"User: {user_input}\n"
        f"Saleem: "
    )
    
    try:
        # response = client.text_generation(prompt, model=MODEL_NAME, max_new_tokens=200, temperature=0.7)
        # return response
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Sorry, I encountered an issue connecting to AI services. Error: {str(e)}"

# Streamlit UI
st.title("Ask Saleem - Your AI Health Assistant 🤖")
st.write("Type your symptoms and chat with Saleem for helpful suggestions!")

# User enters their name
user_name = st.text_input("Enter your name:")

if user_name:
    patient_record = get_patient_record(user_name)
    
    if patient_record:
        st.subheader(f"Patient Record for {user_name}")
        st.write(f"**Age:** {patient_record['Age']}")
        st.write(f"**Gender:** {patient_record['Gender']}")
        st.write(f"**Medical History:** {patient_record['Medical History']}")
        st.write(f"**Current Medications:** {patient_record['Current Medications']}")

        # User enters symptoms manually
        user_symptoms = st.text_area("Describe how you feel:")

        if st.button("Talk to Saleem"):
            if user_symptoms.strip():
                symptoms_list = [symptom.strip().lower() for symptom in user_symptoms.split(",")]
                
                # Correct symptoms using fuzzy matching
                corrected_symptoms = correct_symptoms(symptoms_list)
                
                if corrected_symptoms:
                    st.subheader("Detected Symptoms:")
                    st.write(", ".join(corrected_symptoms))

                    # Find possible diseases
                    possible_diseases = get_possible_diseases(corrected_symptoms)

                    if possible_diseases:
                        st.subheader("Possible Conditions:")
                        st.write(", ".join(possible_diseases))

                        # Get AI-based conversational response
                        st.subheader("Saleem says:")
                        user_input = f"I have symptoms: {', '.join(corrected_symptoms)}."
                        response = get_saleem_response(user_input, corrected_symptoms, patient_record["Medical History"], patient_record["Current Medications"])
                        st.write(response)
                    else:
                        st.warning("Saleem couldn't find a direct match, but let's see what he suggests!")
                        response = get_saleem_response(user_symptoms, [], patient_record["Medical History"], patient_record["Current Medications"])
                        st.write(response)
                else:
                    st.warning("Saleem couldn't recognize the symptoms. Try describing them differently.")
            else:
                st.error("Please describe how you feel.")
    else:
        st.error("Patient record not found. Please check your name or register in the system.")