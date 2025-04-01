from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class PatientInteraction:
    """Represents a single interaction with a patient during follow-up."""
    timestamp: datetime = field(default_factory=datetime.now)
    check_in_message: str = ""
    patient_response: str = ""
    extracted_symptoms: Dict[str, any] = field(default_factory=dict)
    risk_level: str = ""
    risk_justification: str = ""
    care_instructions: str = ""
    summary: str = ""

@dataclass
class Patient:
    """Represents a patient in the dental follow-up system."""
    id: str
    name: str
    procedure: str
    procedure_date: datetime
    contact_info: str
    medical_history: str = ""
    interactions: List[PatientInteraction] = field(default_factory=list)
    
    def add_interaction(self) -> PatientInteraction:
        """Add a new interaction for this patient."""
        interaction = PatientInteraction()
        self.interactions.append(interaction)
        return interaction
    
    def get_latest_interaction(self) -> Optional[PatientInteraction]:
        """Get the most recent interaction for this patient."""
        if not self.interactions:
            return None
        return self.interactions[-1]
