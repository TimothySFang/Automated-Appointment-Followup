from .base_agent import BaseAgent
from config import DENTAL_PROFESSIONAL

class CareInstructionAgent(BaseAgent):
    """Agent responsible for generating personalized care instructions based on symptoms and risk level."""
    
    def __init__(self, name="Care Instruction Agent", api_key=None):
        super().__init__(name, api_key)
    
    def process(self, patient, extracted_symptoms, risk_assessment):
        """Generate personalized care instructions based on symptoms and risk level.
        
        Args:
            patient: The Patient object.
            extracted_symptoms: Dictionary of extracted symptoms from the ResponseAnalyzerAgent.
            risk_assessment: Dictionary containing risk level and justification.
            
        Returns:
            str: Personalized care instructions.
        """
        system_message = (
            "You are a dental professional providing post-operative care instructions. "
            "Your advice should be clear, specific, and tailored to the patient's symptoms and risk level. "
            "For high-risk cases, emphasize the importance of contacting the clinic immediately. "
            "For medium-risk cases, provide specific monitoring instructions. "
            "For low-risk cases, provide reassurance and general care advice."
            "Return plain text and not markdown format"
            "MAKE SURE TO RETURN IN PLAIN TEXT WITH NO MARKDOWN"
        )
         
        is_high_risk = risk_assessment.get('risk_level', '').lower() == 'high'
        
        checkup_link_instruction = ""
        if is_high_risk and 'checkuplink' in DENTAL_PROFESSIONAL:
            checkup_link_instruction = (
                f"\n\nIMPORTANT: Since this is a HIGH RISK situation, include the following link for the patient "
                f"to schedule an immediate appointment: {DENTAL_PROFESSIONAL['checkuplink']}\n"
                f"Make it clear that they should use this link to book an appointment as soon as possible."
            )
        
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
        
        Generate personalized care instructions for this patient based on their symptoms and risk level.
        The instructions should be written directly to the patient in a clear, compassionate tone.
        Include specific advice for managing their symptoms and clear guidance on when to seek professional help.{checkup_link_instruction}
        
        Sign the message with "Warm regards, {DENTAL_PROFESSIONAL['name']}, {DENTAL_PROFESSIONAL['title']}".
        """
        
        care_instructions = self.call_gpt(prompt, system_message)
        
        interaction = patient.get_latest_interaction()
        if interaction:
            interaction.care_instructions = care_instructions
        
        return care_instructions 