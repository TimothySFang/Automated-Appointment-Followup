import os
from abc import ABC, abstractmethod
import openai

class BaseAgent(ABC):
    """Base class for all agents in the dental follow-up system."""

    def __init__(self, name, api_key=None):
        self.name = name

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required.")
        
        self.client = openai.OpenAI(api_key = self.api_key)
    
    @abstractmethod
    def process(self, input_data):
        """Process the input data and return the result
        
        Args:
            input_data: the input data to process
            
            Returns: 
            The processed result.
        """
        pass

    def call_gpt(self, prompt, system_message=None, model="gpt-4o-mini"):
        """Call OpenAI GPT API with prompt
        
        Args:
            prompt: user prompt to send to api
            system_message: Optional system message to set context.
            model: the model to use (default with gpt-3.5-turbo)

        Returns:
            the response from API    
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )

        return response.choices[0].message.content