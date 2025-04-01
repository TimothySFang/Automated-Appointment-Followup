import streamlit as st
import os
from datetime import datetime, timedelta
import json

from models.patient import Patient
from agents.symptom_checkin import SymptomCheckInAgent
from agents.response_analyzer import ResponseAnalyzerAgent
from agents.risk_assessment import RiskAssessmentAgent
from agents.care_instruction import CareInstructionAgent
from agents.summary import SummaryAgent

# Page configuration
st.set_page_config(
    page_title="Autonomous Dental Follow-Up & Risk Monitor",
    page_icon="🦷",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'patient' not in st.session_state:
    st.session_state.patient = None
if 'check_in_message' not in st.session_state:
    st.session_state.check_in_message = None
if 'patient_response' not in st.session_state:
    st.session_state.patient_response = ""
if 'extracted_symptoms' not in st.session_state:
    st.session_state.extracted_symptoms = None
if 'risk_assessment' not in st.session_state:
    st.session_state.risk_assessment = None
if 'care_instructions' not in st.session_state:
    st.session_state.care_instructions = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY environment variable is not set. Please set it before running the app.")
    st.stop()

# Title and description
st.title("Autonomous Dental Follow-Up & Risk Monitor")
st.markdown("""
This prototype demonstrates an AI-powered system for post-procedure follow-up in dental clinics.
The system uses a swarm of specialized AI agents to check in with patients, analyze their responses,
assess risk, and provide appropriate care instructions.
""")

# Sidebar for patient information
with st.sidebar:
    st.header("Patient Information")
    
    # Patient information form
    with st.form("patient_info"):
        patient_name = st.text_input("Patient Name", value="John Doe")
        procedure = st.selectbox(
            "Procedure",
            ["Wisdom Tooth Extraction", "Root Canal", "Dental Implant", "Crown Placement", "Gum Surgery"]
        )
        procedure_date = st.date_input(
            "Procedure Date",
            value=datetime.now() - timedelta(days=2)
        )
        medical_history = st.text_area(
            "Medical History",
            value="No significant medical history. No known allergies."
        )
        contact_info = st.text_input("Contact Info", value="john.doe@example.com")
        
        submit_button = st.form_submit_button("Create/Update Patient")
        
        if submit_button:
            # Create a new patient
            st.session_state.patient = Patient(
                id=f"P{datetime.now().strftime('%Y%m%d%H%M%S')}",
                name=patient_name,
                procedure=procedure,
                procedure_date=datetime.combine(procedure_date, datetime.min.time()),
                contact_info=contact_info,
                medical_history=medical_history
            )
            st.session_state.patient.add_interaction()
            st.session_state.current_step = 1
            st.session_state.check_in_message = None
            st.session_state.patient_response = ""
            st.session_state.extracted_symptoms = None
            st.session_state.risk_assessment = None
            st.session_state.care_instructions = None
            st.session_state.summary = None
            st.success("Patient created successfully!")

# Main content area
if not st.session_state.patient:
    st.info("Please create a patient using the form in the sidebar.")
else:
    # Create tabs for each step in the workflow
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1. Check-In Message", 
        "2. Symptom Analysis", 
        "3. Risk Assessment",
        "4. Care Instructions",
        "5. Clinic Summary"
    ])
    
    # Tab 1: Check-In Message
    with tab1:
        st.header("Step 1: Generate Check-In Message")
        
        if st.button("Generate Check-In Message", key="gen_checkin"):
            with st.spinner("Generating check-in message..."):
                # Create the agent with the API key from session state
                symptom_checkin_agent = SymptomCheckInAgent(api_key=api_key)
                
                # Generate the check-in message
                st.session_state.check_in_message = symptom_checkin_agent.process(st.session_state.patient)
                st.session_state.current_step = 2
        
        if st.session_state.check_in_message:
            st.subheader("Check-In Message:")
            st.info(st.session_state.check_in_message)
    
    # Tab 2: Symptom Analysis
    with tab2:
        st.header("Step 2: Analyze Patient Response")
        
        if not st.session_state.check_in_message:
            st.warning("Please generate a check-in message first.")
        else:
            st.subheader("Patient Response:")
            patient_response = st.text_area(
                "Enter the patient's response:",
                value=st.session_state.patient_response,
                height=150
            )
            
            if st.button("Analyze Response", key="analyze_response"):
                if not patient_response:
                    st.error("Please enter a patient response.")
                else:
                    with st.spinner("Analyzing patient response..."):
                        # Update the session state
                        st.session_state.patient_response = patient_response
                        
                        # Create the agent with the API key from session state
                        response_analyzer_agent = ResponseAnalyzerAgent(api_key=api_key)
                        
                        # Analyze the response
                        st.session_state.extracted_symptoms = response_analyzer_agent.process(
                            st.session_state.patient, 
                            st.session_state.patient_response
                        )
                        st.session_state.current_step = 3
            
            if st.session_state.extracted_symptoms:
                st.subheader("Extracted Symptoms:")
                
                # Display the extracted symptoms in a more readable format
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Pain Level", st.session_state.extracted_symptoms.get("pain_level", "Not mentioned"))
                    st.metric("Bleeding", st.session_state.extracted_symptoms.get("bleeding", "Not mentioned"))
                    st.metric("Swelling", st.session_state.extracted_symptoms.get("swelling", "Not mentioned"))
                    st.metric("Fever", "Yes" if st.session_state.extracted_symptoms.get("fever", False) else "No")
                
                with col2:
                    st.metric("Medication Taken", st.session_state.extracted_symptoms.get("medication_taken", "None"))
                    st.metric("Overall Sentiment", st.session_state.extracted_symptoms.get("overall_sentiment", "Not analyzed"))
                    
                    # Display other symptoms as a list
                    other_symptoms = st.session_state.extracted_symptoms.get("other_symptoms", [])
                    if other_symptoms:
                        st.write("**Other Symptoms:**")
                        for symptom in other_symptoms:
                            st.write(f"- {symptom}")
                    else:
                        st.write("**Other Symptoms:** None")
                    
                    # Display patient concerns
                    st.write("**Patient Concerns:**")
                    st.write(st.session_state.extracted_symptoms.get("patient_concerns", "None"))
    
    # Tab 3: Risk Assessment
    with tab3:
        st.header("Step 3: Risk Assessment")
        
        if not st.session_state.extracted_symptoms:
            st.warning("Please analyze a patient response first.")
        else:
            if st.button("Assess Risk", key="assess_risk"):
                with st.spinner("Assessing risk level..."):
                    # Create the agent with the API key from session state
                    risk_assessment_agent = RiskAssessmentAgent(api_key=api_key)
                    
                    # Assess the risk
                    st.session_state.risk_assessment = risk_assessment_agent.process(
                        st.session_state.patient, 
                        st.session_state.extracted_symptoms
                    )
                    st.session_state.current_step = 4
            
            if st.session_state.risk_assessment:
                risk_level = st.session_state.risk_assessment.get("risk_level", "Unknown")
                
                # Display the risk level with appropriate color
                if risk_level.lower() == "low":
                    st.success(f"Risk Level: {risk_level}")
                elif risk_level.lower() == "medium":
                    st.warning(f"Risk Level: {risk_level}")
                elif risk_level.lower() == "high":
                    st.error(f"Risk Level: {risk_level}")
                else:
                    st.info(f"Risk Level: {risk_level}")
                
                # Display the justification
                st.subheader("Justification:")
                st.write(st.session_state.risk_assessment.get("justification", "No justification provided."))
    
    # Tab 4: Care Instructions
    with tab4:
        st.header("Step 4: Care Instructions")
        
        if not st.session_state.risk_assessment:
            st.warning("Please complete the risk assessment first.")
        else:
            if st.button("Generate Care Instructions", key="gen_care"):
                with st.spinner("Generating care instructions..."):
                    # Create the agent with the API key from session state
                    care_instruction_agent = CareInstructionAgent(api_key=api_key)
                    
                    # Generate care instructions
                    st.session_state.care_instructions = care_instruction_agent.process(
                        st.session_state.patient,
                        st.session_state.extracted_symptoms,
                        st.session_state.risk_assessment
                    )
                    st.session_state.current_step = 5
            
            if st.session_state.care_instructions:
                st.subheader("Care Instructions:")
                st.write(st.session_state.care_instructions)
    
    # Tab 5: Clinic Summary
    with tab5:
        st.header("Step 5: Clinic Summary")
        
        if not st.session_state.care_instructions:
            st.warning("Please generate care instructions first.")
        else:
            if st.button("Generate Clinic Summary", key="gen_summary"):
                with st.spinner("Generating clinic summary..."):
                    # Create the agent with the API key from session state
                    summary_agent = SummaryAgent(api_key=api_key)
                    
                    # Generate summary
                    st.session_state.summary = summary_agent.process(
                        st.session_state.patient,
                        st.session_state.extracted_symptoms,
                        st.session_state.risk_assessment,
                        st.session_state.care_instructions
                    )
            
            if st.session_state.summary:
                st.subheader("Clinic Summary:")
                st.write(st.session_state.summary)
                
                # Display a success message when the workflow is complete
                st.success("Patient follow-up workflow completed successfully!")

# Footer
st.markdown("---")
st.markdown("Autonomous Dental Follow-Up & Risk Monitor - Prototype")