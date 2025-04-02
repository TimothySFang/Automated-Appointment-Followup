from .base_agent import BaseAgent
from config import DENTAL_PROFESSIONAL

class SymptomCheckInAgent(BaseAgent):
    """Agent responsible for generating personalized check-in messages for patients"""

    def __init__(self, name="Symptom Check-in Agent", api_key=None):
        super().__init__(name, api_key)
    
    def process(self, patient):
        """Generate a personalized check-in message for the patient
        
        Args:
            patient: The Patient object to generate a check-in message for.
            
        Returns:
            str: A personalized check-in message
        """

        system_message = (
            f"You are a friendly dental assistant from {DENTAL_PROFESSIONAL['clinic_name']} checking in on patients after their procedure. "
            "Your tone should be warm, professional, and reassuring. "
            "Ask specifically about pain, bleeding, swelling, and any concerns that are of similar nature."
            "Return plain text and not markdown format"
        )

        prompt = f"""
        Generate a personalized check-in message for a patient who had {patient.procedure} 
        on {patient.procedure_date.strftime('%Y-%m-%d')}. 
        
        Patient name: {patient.name}
        Medical history: {patient.medical_history}
        
        The message should ask how they're feeling and if they're experiencing any concerning symptoms.
        
        Sign the message with "Best regards, {DENTAL_PROFESSIONAL['name']}, {DENTAL_PROFESSIONAL['title']}"
        and include the clinic name "{DENTAL_PROFESSIONAL['clinic_name']}" in the signature.
        """
        
        # Call the GPT API to generate the check-in message
        check_in_message = self.call_gpt(prompt, system_message)
        
        # Store the message in the patient's latest interaction
        interaction = patient.get_latest_interaction()
        if interaction:
            interaction.check_in_message = check_in_message
        
        return check_in_message
