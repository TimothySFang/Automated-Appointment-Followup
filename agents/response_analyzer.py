from .base_agent import BaseAgent

class ResponseAnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing patient responses and extracting structured symptom data."""
    
    def __init__(self, name="Response Analyzer Agent", api_key=None):
        super().__init__(name, api_key)
    
    def process(self, patient, response_text):
        """Analyze a patient's response and extract structured symptom data.
        
        Args:
            patient: The Patient object.
            response_text: The text response from the patient.
            
        Returns:
            dict: Structured data about the patient's symptoms.
        """
        # Create a system message that guides the AI's behavior
        system_message = (
            "You are a dental professional analyzing patient responses after procedures. "
            "Extract specific symptoms and their severity from the patient's message. "
            "Focus on pain (scale 1-10), bleeding (none/mild/moderate/severe), "
            "swelling (none/mild/moderate/severe), fever, and any other symptoms mentioned."
        )
        
        # Create a prompt with patient context and their response
        prompt = f"""
        Patient: {patient.name}
        Procedure: {patient.procedure}
        Procedure Date: {patient.procedure_date.strftime('%Y-%m-%d')}
        Medical History: {patient.medical_history}
        
        Patient's Response: "{response_text}"
        
        Extract the following information in JSON format:
        {{
            "pain_level": (integer 0-10 or "none" if not mentioned),
            "bleeding": ("none", "mild", "moderate", "severe", or "not mentioned"),
            "swelling": ("none", "mild", "moderate", "severe", or "not mentioned"),
            "fever": (true/false),
            "medication_taken": (string or "none"),
            "other_symptoms": (array of strings or empty array),
            "patient_concerns": (string or "none"),
            "overall_sentiment": ("positive", "neutral", "concerned", "negative")
        }}
        
        Provide ONLY the JSON with no additional text.
        """
        
        # Call the GPT API to analyze the response
        analysis_result = self.call_gpt(prompt, system_message)
        
        # Try to parse the result as a dictionary (it should be JSON)
        try:
            import json
            extracted_symptoms = json.loads(analysis_result)
        except json.JSONDecodeError:
            # If parsing fails, return a basic structure with an error
            extracted_symptoms = {
                "error": "Failed to parse response",
                "raw_response": analysis_result
            }
        
        # Store the extracted symptoms in the patient's latest interaction
        interaction = patient.get_latest_interaction()
        if interaction:
            interaction.patient_response = response_text
            interaction.extracted_symptoms = extracted_symptoms
        
        return extracted_symptoms
