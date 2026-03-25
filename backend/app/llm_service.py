import os
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class LLMService:
    def __init__(self):
        """Initialize Gemini LLM service with available models"""
        # Get API key from environment
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure the API
        try:
            genai.configure(api_key=self.api_key)
            
            # Use the new available models
            # Try the latest models in order of preference
            models_to_try = [
                'models/gemini-2.5-flash',      # Fast and capable
                'models/gemini-2.0-flash',       # Stable
                'models/gemini-flash-latest',    # Latest flash
                'models/gemini-2.5-pro',         # Most powerful
            ]
            
            working_model = None
            for model_name in models_to_try:
                try:
                    print(f"Testing model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    # Test the model with a simple prompt
                    response = model.generate_content("Say 'OK'")
                    if response and response.text:
                        working_model = model_name
                        self.model = model
                        print(f"✅ Connected with model: {working_model}")
                        break
                except Exception as e:
                    print(f"   {model_name} failed: {str(e)[:80]}")
                    continue
            
            if not working_model:
                # Fallback to list models dynamically
                print("Trying to find any working model...")
                for model in genai.list_models():
                    if 'generateContent' in model.supported_generation_methods:
                        try:
                            test_model = genai.GenerativeModel(model.name)
                            response = test_model.generate_content("Test")
                            if response and response.text:
                                working_model = model.name
                                self.model = test_model
                                print(f"✅ Connected with model: {working_model}")
                                break
                        except:
                            continue
                
            if not working_model:
                raise Exception("No working Gemini model found. Please check your API key.")
                
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini client: {str(e)}")
        
        self.provider = "gemini"
        self.model_name = working_model
    
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """Send document text to Gemini and get structured analysis"""
        
        # Truncate text if too long (Gemini 2.5 has larger context, but let's be safe)
        max_chars = 50000  # Increased for newer models
        if len(text) > max_chars:
            text = text[:max_chars] + "... (truncated)"
        
        # Create prompt for Gemini
        prompt = f"""
        Analyze the following document and extract key information.
        
        Document text:
        {text}
        
        Please provide:
        1. TITLE: What is the main title of this document?
        2. AUTHOR: Who is the author (if mentioned)? If not found, state "Unknown"
        3. SUMMARY: A concise 2-3 sentence summary of the main content
        
        Format your response exactly like this:
        TITLE: [title]
        AUTHOR: [author]
        SUMMARY: [summary]
        
        Be concise and accurate.
        """
        
        try:
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 500,
                }
            )
            
            # Get response text
            if response and response.text:
                result_text = response.text
                return self._parse_response(result_text)
            else:
                return {
                    "title": "No response from AI",
                    "author": "Unknown",
                    "summary": "The AI model did not return a response. Please try again.",
                    "error": True
                }
                
        except Exception as e:
            error_message = str(e)
            print(f"Gemini API error: {error_message}")
            return {
                "title": "Analysis Failed",
                "author": "Unknown",
                "summary": f"Error analyzing document: {error_message}",
                "error": True
            }
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured format"""
        result = {
            "title": "Not detected",
            "author": "Unknown",
            "summary": "No summary available"
        }
        
        # Split into lines and parse
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('TITLE:'):
                result["title"] = line.replace('TITLE:', '').strip()
            elif line.startswith('AUTHOR:'):
                result["author"] = line.replace('AUTHOR:', '').strip()
            elif line.startswith('SUMMARY:'):
                result["summary"] = line.replace('SUMMARY:', '').strip()
        
        # If parsing failed but we have a response, try a fallback approach
        if result["title"] == "Not detected" and len(response_text) > 0:
            # Try to intelligently extract
            if "title" in response_text.lower():
                result["summary"] = response_text[:500]
        
        return result
    
    def test_connection(self) -> bool:
        """Test if Gemini API is working"""
        try:
            response = self.model.generate_content("Say 'Connection successful'")
            return response and response.text is not None
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False