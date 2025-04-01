from .base_agent import BaseAgent
from config import DENTAL_PROFESSIONAL

class SummaryAgent(BaseAgent):
    """Agent responsible for generating a clinical summary of the patient interaction."""
    
    def __init__(self, name="Summary Agent", api_key=None):
        super().__init__(name, api_key)
    
    def process(self, patient, extracted_symptoms, risk_assessment, care_instructions):
        """Generate a clinical summary of the patient interaction.
        
        Args:
            patient: The Patient object.
            extracted_symptoms: Dictionary of extracted symptoms.
            risk_assessment: Dictionary containing risk level and justification.
            care_instructions: The care instructions provided to the patient.
            
        Returns:
            str: Clinical summary.
        """
        # Create a system message that guides the AI's behavior
        system_message = (
            f"You are {DENTAL_PROFESSIONAL['name']}, {DENTAL_PROFESSIONAL['title']} at {DENTAL_PROFESSIONAL['clinic_name']}, "
            "creating a clinical summary for a patient's dental follow-up. "
            "Your summary should be professional, concise, and include all relevant clinical information. "
            "Format the summary with clear sections for symptoms, assessment, care provided, and follow-up recommendations."
        )
        
        # Create a prompt with all the context
        prompt = f"""
        Patient: {patient.name}
        Procedure: {patient.procedure}
        Procedure Date: {patient.procedure_date.strftime('%Y-%m-%d')}
        Medical History: {patient.medical_history}
        
        Extracted Symptoms:
        - Pain Level: {extracted_symptoms.get('pain_level', 'Not mentioned')}
        - Bleeding: {extracted_symptoms.get('bleeding', 'Not mentioned')}
        - Swelling: {extracted_symptoms.get('swelling', 'Not mentioned')}
        - Fever: {extracted_symptoms.get('fever', False)}
        - Medication Taken: {extracted_symptoms.get('medication_taken', 'None')}
        - Other Symptoms: {', '.join(extracted_symptoms.get('other_symptoms', [])) or 'None'}
        
        Risk Assessment:
        - Risk Level: {risk_assessment.get('risk_level', 'Unknown')}
        - Justification: {risk_assessment.get('justification', 'Not provided')}
        
        Care Instructions Provided:
        {care_instructions}
        
        Generate a comprehensive clinical summary of this follow-up interaction.
        Include relevant symptoms, your assessment, care instructions provided, and any recommended follow-up.
        This summary will be added to the patient's medical record.
        """
        
        # Call the GPT API to generate the summary
        summary = self.call_gpt(prompt, system_message)
        
        # Store the summary in the patient's latest interaction
        interaction = patient.get_latest_interaction()
        if interaction:
            interaction.summary = summary
        
        return summary 