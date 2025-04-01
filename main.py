import os
from datetime import datetime, timedelta
from models.patient import Patient
from agents.symptom_checkin import SymptomCheckInAgent
from agents.response_analyzer import ResponseAnalyzerAgent
from agents.risk_assessment import RiskAssessmentAgent
from agents.care_instruction import CareInstructionAgent
from agents.summary import SummaryAgent

def main():
    # Get OpenAI API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return
    
    # Create the agents
    symptom_checkin_agent = SymptomCheckInAgent(api_key=api_key)
    response_analyzer_agent = ResponseAnalyzerAgent(api_key=api_key)
    risk_assessment_agent = RiskAssessmentAgent(api_key=api_key)
    care_instruction_agent = CareInstructionAgent(api_key=api_key)
    summary_agent = SummaryAgent(api_key=api_key)
    
    # Create a sample patient
    patient = Patient(
        id="P12345",
        name="John Doe",
        procedure="Wisdom Tooth Extraction",
        procedure_date=datetime.now() - timedelta(days=2),
        contact_info="john.doe@example.com",
        medical_history="No significant medical history. No known allergies."
    )
    
    # Add a new interaction
    patient.add_interaction()
    
    # Step 1: Generate check-in message
    print("\n=== Step 1: Check-In Message ===")
    check_in_message = symptom_checkin_agent.process(patient)
    print(check_in_message)
    
    # Step 2: Simulate patient response (in a real app, this would come from the patient)
    print("\n=== Step 2: Patient Response ===")
    patient_response = """
    Hi, thanks for checking in. I'm feeling okay but still have some pain, about a 6 out of 10. 
    The bleeding has mostly stopped, just a little bit when I brush my teeth. 
    My cheek is still pretty swollen though. I've been taking the prescribed pain medication.
    I'm a bit worried about the swelling - is it normal for it to still be this swollen after 2 days?
    """
    print(patient_response)
    
    # Step 3: Analyze patient response
    print("\n=== Step 3: Symptom Analysis ===")
    extracted_symptoms = response_analyzer_agent.process(patient, patient_response)
    print("Extracted Symptoms:")
    for key, value in extracted_symptoms.items():
        print(f"- {key}: {value}")
    
    # Step 4: Assess risk
    print("\n=== Step 4: Risk Assessment ===")
    risk_assessment = risk_assessment_agent.process(patient, extracted_symptoms)
    print(f"Risk Level: {risk_assessment.get('risk_level')}")
    print(f"Justification: {risk_assessment.get('justification')}")
    
    # Step 5: Generate care instructions
    print("\n=== Step 5: Care Instructions ===")
    care_instructions = care_instruction_agent.process(patient, extracted_symptoms, risk_assessment)
    print(care_instructions)
    
    # Step 6: Generate summary for clinic
    print("\n=== Step 6: Clinic Summary ===")
    summary = summary_agent.process(patient, extracted_symptoms, risk_assessment, care_instructions)
    print(summary)
    
    # Print the complete interaction record
    print("\n=== Complete Patient Interaction Record ===")
    interaction = patient.get_latest_interaction()
    print(f"Timestamp: {interaction.timestamp}")
    print(f"Risk Level: {interaction.risk_level}")

if __name__ == "__main__":
    main()
