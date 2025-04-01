from .base_agent import BaseAgent

class SummaryAgent(BaseAgent):
    """Agent responsible for generating a clinic-facing summary of the patient interaction."""
    
    def __init__(self, name="Summary Agent", api_key=None):
        super().__init__(name, api_key)
    
    def process(self, patient, extracted_symptoms, risk_assessment, care_instructions):
        """Generate a clinic-facing summary of the patient interaction.
        
        Args:
            patient: The Patient object.
            extracted_symptoms: Dictionary of extracted symptoms from the ResponseAnalyzerAgent.
            risk_assessment: Dictionary containing risk level and justification.
            care_instructions: String containing the care instructions provided to the patient.
            
        Returns:
            str: A clinic-facing summary of the interaction.
        """
        # Create a system message that guides the AI's behavior
        system_message = (
            "You are a dental professional summarizing patient follow-up interactions for clinic staff. "
            "Your summary should be concise, professional, and highlight key clinical information. "
            "Focus on symptoms, risk assessment, and any actions that may be needed from the clinic."
        )
        
        # Create a prompt with all the interaction details
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
        - Patient Concerns: {extracted_symptoms.get('patient_concerns', 'None')}
        - Overall Sentiment: {extracted_symptoms.get('overall_sentiment', 'Not analyzed')}
        
        Risk Assessment:
        - Risk Level: {risk_assessment.get('risk_level', 'Unknown')}
        - Justification: {risk_assessment.get('justification', 'Not provided')}
        
        Care Instructions Provided:
        {care_instructions}
        
        Generate a concise, clinic-facing summary of this patient interaction.
        Highlight any concerning symptoms, the risk level, and whether any follow-up from the clinic is recommended.
        The summary should be professional and focused on clinical relevance.
        """
        
        # Call the GPT API to generate the summary
        summary = self.call_gpt(prompt, system_message)
        
        # Store the summary in the patient's latest interaction
        interaction = patient.get_latest_interaction()
        if interaction:
            interaction.summary = summary
        
        return summary 