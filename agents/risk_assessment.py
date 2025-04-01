from .base_agent import BaseAgent

class RiskAssessmentAgent(BaseAgent):
    """Agent responsible for assessing the risk level based on patient symptoms."""
    
    def __init__(self, name="Risk Assessment Agent", api_key=None):
        super().__init__(name, api_key)
    
    def process(self, patient, extracted_symptoms):
        """Assess the risk level based on the patient's symptoms.
        
        Args:
            patient: The Patient object.
            extracted_symptoms: Dictionary of extracted symptoms from the ResponseAnalyzerAgent.
            
        Returns:
            dict: Risk assessment with level and justification.
        """
        # Create a system message that guides the AI's behavior
        system_message = (
            "You are a dental professional specializing in post-operative risk assessment. "
            "Evaluate the patient's symptoms and classify their condition as Low, Medium, or High risk. "
            "Consider the type of procedure, time since procedure, and severity of symptoms. "
            "Provide clear justification for your risk assessment."
        )
        
        # Create a prompt with patient context and their symptoms
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
        
        Assess the risk level for this patient based on their symptoms and provide justification.
        Return your assessment in JSON format:
        {{
            "risk_level": ("Low", "Medium", or "High"),
            "justification": (detailed explanation of your assessment)
        }}
        
        Provide ONLY the JSON with no additional text.
        """
        
        # Call the GPT API to assess the risk
        assessment_result = self.call_gpt(prompt, system_message)
        
        # Try to parse the result as a dictionary (it should be JSON)
        try:
            import json
            risk_assessment = json.loads(assessment_result)
        except json.JSONDecodeError:
            # If parsing fails, return a basic structure with an error
            risk_assessment = {
                "risk_level": "Unknown",
                "justification": "Error in risk assessment",
                "error": "Failed to parse response",
                "raw_response": assessment_result
            }
        
        # Store the risk assessment in the patient's latest interaction
        interaction = patient.get_latest_interaction()
        if interaction:
            interaction.risk_level = risk_assessment.get("risk_level", "Unknown")
            interaction.risk_justification = risk_assessment.get("justification", "")
        
        return risk_assessment