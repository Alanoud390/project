import streamlit as st 
from huggingface_hub import InferenceClient
import pandas as pd
import os

# Excel file path
excel_file = "patients_data.xlsx"

# Load existing data if file exists
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
    patients_data = df.to_dict(orient="records")
else:
    patients_data = []

# Function to collect and update patient data
def collect_patient_data():
    st.title("Patient Data Entry")

    name = st.text_input("Patient Name:")
    age = st.number_input("Age:", min_value=0, max_value=99, step=1)
    gender = st.selectbox("Gender:", ["Male", "Female"])
    medical_history = st.text_area("Medical History:")
    current_medications = st.text_area("Current Medications:")

    if st.button("Save Data"):
        # Check if the patient already exists in the data
        existing_patient = next((p for p in patients_data if p["Name"] == name), None)
        
        if existing_patient:
            # Update existing patient data
            existing_patient["Age"] = age
            existing_patient["Gender"] = gender
            existing_patient["Medical History"] = medical_history
            existing_patient["Current Medications"] = current_medications
            st.success("Patient data updated successfully!")
        else:
            # Add new patient
            patient = {
                "Name": name,
                "Age": age,
                "Gender": gender,
                "Medical History": medical_history,
                "Current Medications": current_medications
            }
            patients_data.append(patient)
            st.success("New patient data saved successfully!")
        
        save_to_excel()  # Automatically save to Excel

# Function to save data to an Excel file automatically
def save_to_excel():
    df = pd.DataFrame(patients_data)
    df.to_excel(excel_file, index=False)

# Run the app
collect_patient_data()