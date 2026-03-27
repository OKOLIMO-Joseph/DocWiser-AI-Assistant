import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


class LLMService:
    def __init__(self):
        """Initialize Gemini LLM service with available models"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self._initialize_model()
        self.provider = "gemini"
    
    def _initialize_model(self):
        """Initialize Gemini client and find a working model"""
        try:
            genai.configure(api_key=self.api_key)
            
            models_to_try = [
                'models/gemini-2.5-flash',
                'models/gemini-2.0-flash',
                'models/gemini-flash-latest',
                'models/gemini-2.5-pro',
            ]
            
            working_model = None
            for model_name in models_to_try:
                try:
                    print(f"Testing model: {model_name}")
                    model = genai.GenerativeModel(model_name)
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
                raise Exception("No working Gemini model found. Please check your API key.")
                
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini client: {str(e)}")
        
        self.model_name = working_model
    
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """Send document text to Gemini and get structured analysis"""
        
        # Truncate text if too long
        max_chars = 50000
        if len(text) > max_chars:
            text = text[:max_chars] + "... (truncated)"
        
        # Clean prompt with explicit formatting instructions
        prompt = f"""
Analyze the following document and extract:

1. TITLE - The main title of the document
2. AUTHOR - The author(s) if mentioned, otherwise "Unknown"  
3. SUMMARY - A 2-3 sentence summary of the main content

IMPORTANT: Format your response EXACTLY like this with the labels:

TITLE: [insert title here]
AUTHOR: [insert author here]
SUMMARY: [insert 2-3 sentence summary here]

Do not add any other text or explanations.

Document:
{text}
"""
        
        try:
            # Generate response with increased token limit
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 1000,  # Increased from 500 to 1000
                }
            )
            
            # Debug: Print raw response
            print("=" * 50)
            print("RAW GEMINI RESPONSE:")
            raw_text = response.text if response else "No response"
            print(raw_text)
            print("=" * 50)
            
            if response and response.text:
                result_text = response.text
                
                # Check if response was truncated
                if self._is_truncated(result_text):
                    print("⚠️ Response appears truncated - retrying...")
                    # Retry with higher token limit
                    response = self.model.generate_content(
                        prompt,
                        generation_config={
                            "temperature": 0.3,
                            "max_output_tokens": 1500,  # Even higher for retry
                        }
                    )
                    if response and response.text:
                        result_text = response.text
                
                return self._parse_response(result_text)
            else:
                return self._error_response("No response from AI model")
                
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            return self._error_response(f"AI analysis failed: {str(e)}")
    
    def _is_truncated(self, response: str) -> bool:
        """Check if response appears to be truncated mid-summary"""
        # Check if response ends with incomplete sentence
        if not response:
            return False
        
        # Common truncation indicators
        truncated_endings = [
            '...', '.', '!', '?', '"', "'", '`', 
            'The', 'This', 'It', 'In', 'The document'
        ]
        
        last_char = response.strip()[-1] if response.strip() else ''
        
        # If response doesn't end with proper punctuation, might be truncated
        if last_char not in ['.', '!', '?', '"', "'"]:
            # Also check if it's cut off mid-word
            if response.strip().endswith(('-', '_', ' ')):
                return True
            # Check if last line is incomplete
            last_line = response.strip().split('\n')[-1]
            if last_line and not last_line.endswith(('.', '!', '?')):
                return True
        
        return False
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured format"""
        result = {
            "title": "Not detected",
            "author": "Unknown",
            "summary": "No summary available"
        }
        
        response_text = response_text.strip()
        lines = response_text.split('\n')
        
        # Parse line by line
        current_section = None
        section_content = []
        
        for line in lines:
            line = line.strip()
            lower = line.lower()
            
            # Detect section headers
            if lower.startswith('title:'):
                if current_section == 'summary' and section_content:
                    result["summary"] = ' '.join(section_content).strip()
                current_section = 'title'
                section_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif lower.startswith('author:'):
                if current_section == 'title' and section_content:
                    result["title"] = ' '.join(section_content).strip()
                current_section = 'author'
                section_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif lower.startswith('summary:'):
                if current_section == 'author' and section_content:
                    result["author"] = ' '.join(section_content).strip()
                current_section = 'summary'
                section_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif current_section and line:
                # Continue multi-line content
                section_content.append(line)
        
        # Save last section
        if current_section == 'title' and section_content:
            result["title"] = ' '.join(section_content).strip()
        elif current_section == 'author' and section_content:
            result["author"] = ' '.join(section_content).strip()
        elif current_section == 'summary' and section_content:
            result["summary"] = ' '.join(section_content).strip()
        
        # Clean up
        result["title"] = self._clean_text(result["title"])
        result["author"] = self._clean_text(result["author"])
        result["summary"] = self._clean_text(result["summary"])
        
        # Fallback if parsing failed
        if result["title"] == "Not detected" and len(lines) > 0:
            # Try first non-empty line as title
            for line in lines:
                clean = line.strip()
                if clean and len(clean) < 100:
                    result["title"] = clean
                    break
        
        if result["summary"] == "No summary available" and len(response_text) > 100:
            # Try last paragraph as summary
            paragraphs = [p.strip() for p in response_text.split('\n\n') if p.strip()]
            if paragraphs:
                result["summary"] = paragraphs[-1][:500]
        
        # Debug output
        print("PARSED RESULT:")
        print(f"  Title: {result['title'][:100]}")
        print(f"  Author: {result['author']}")
        print(f"  Summary: {result['summary'][:200]}...")
        print("=" * 50)
        
        return result
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Remove formatting artifacts from text"""
        if not text:
            return text
        # Remove markdown and extra spaces
        text = text.replace('*', '').replace('**', '').replace('_', '')
        text = text.replace('###', '').replace('##', '').replace('#', '')
        # Collapse multiple spaces
        text = ' '.join(text.split())
        return text.strip()
    
    @staticmethod
    def _error_response(message: str) -> Dict[str, Any]:
        """Return standardized error response"""
        return {
            "title": "Analysis Failed",
            "author": "Unknown",
            "summary": message,
            "error": True
        }
    
    def test_connection(self) -> bool:
        """Test if Gemini API is working"""
        try:
            response = self.model.generate_content("Say 'Connection successful'")
            return response and response.text is not None
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False