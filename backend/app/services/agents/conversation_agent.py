"""
Conversational IT Support Agent
Asks clarifying questions like a real IT technician to debug issues properly.
"""
import logging
from typing import List, Dict, Optional
import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ConversationAgent:
    """
    Agent that conducts natural troubleshooting conversations.
    Mimics how real IT technicians debug issues by asking questions.
    """
    
    def __init__(self):
        """Initialize Gemini for conversations."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        genai.configure(api_key=settings.google_api_key)
        # Use gemini-1.5-pro (stable model) instead of flash
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        logger.info("Conversation Agent initialized")
    
    def analyze_issue_clarity(self, description: str) -> Dict:
        """
        Determine if issue description is clear enough to proceed.
        Uses keyword-based analysis for reliability.
        
        Returns:
            {
                "is_clear": bool,
                "confidence": float,
                "needs_clarification": bool,
                "clarifying_questions": List[str],
                "initial_category": str
            }
        """
        desc_lower = description.lower()
        word_count = len(description.split())
        
        # Check for IT-related keywords
        it_keywords = [
            'slow', 'error', 'crash', 'blue screen', 'bsod', 'freeze', 'hang',
            'vpn', 'network', 'wifi', 'internet', 'connection', 'login', 'password',
            'outlook', 'teams', 'chrome', 'software', 'install', 'update',
            'laptop', 'computer', 'mouse', 'keyboard', 'monitor', 'printer',
            'access', 'permission', 'denied', 'cant', "can't", 'unable', 'not working'
        ]
        
        has_it_issue = any(keyword in desc_lower for keyword in it_keywords)
        
        # Very short messages like "hi", "hello", "help" need clarification
        greeting_words = ['hi', 'hello', 'hey', 'help', 'okay', 'ok', 'thanks', 'thank you']
        is_greeting = desc_lower.strip() in greeting_words or word_count < 3
        
        # Determine if clear enough
        is_clear = has_it_issue and not is_greeting and word_count >= 5
        
        if is_clear:
            return {
                "is_clear": True,
                "confidence": 0.8,
                "needs_clarification": False,
                "clarifying_questions": [],
                "initial_category": self._quick_categorize(desc_lower),
                "reasoning": "Issue description has sufficient detail"
            }
        else:
            return {
                "is_clear": False,
                "confidence": 0.6,
                "needs_clarification": True,
                "clarifying_questions": [
                    "What specific issue are you experiencing?",
                    "When did this problem start?",
                    "Are there any error messages displayed?"
                ],
                "initial_category": "other",
                "reasoning": "Need more details about the issue"
            }
    
    def _quick_categorize(self, desc_lower: str) -> str:
        """Quick keyword-based categorization."""
        if any(kw in desc_lower for kw in ['vpn', 'network', 'wifi', 'internet', 'connection']):
            return 'network'
        elif any(kw in desc_lower for kw in ['bsod', 'blue screen', 'crash', 'hardware']):
            return 'hardware'
        elif any(kw in desc_lower for kw in ['slow', 'freeze', 'hang', 'performance']):
            return 'performance'
        elif any(kw in desc_lower for kw in ['login', 'password', 'access', 'permission']):
            return 'access'
        elif any(kw in desc_lower for kw in ['outlook', 'teams', 'chrome', 'software', 'app']):
            return 'software'
        return 'other'
    
    def generate_clarifying_questions(
        self,
        description: str,
        category: str,
        conversation_history: List[Dict] = None
    ) -> List[str]:
        """
        Generate smart clarifying questions based on issue type.
        Like what a real IT technician would ask.
        """
        
        # Category-specific question templates
        templates = {
            "network": [
                "Are you on WiFi or wired ethernet?",
                "Can you access any other websites or internal services?",
                "When did this problem start?",
                "Did anything change (password, location, updates)?"
            ],
            "hardware": [
                "When did this issue start?",
                "Does it happen all the time or intermittently?",
                "Have you dropped or physically damaged the device recently?",
                "Does it work when plugged directly (not through dock/hub)?"
            ],
            "software": [
                "Which specific program is having the issue?",
                "When did this start happening?",
                "Did you recently install any updates or new software?",
                "Does the same issue happen with other programs?"
            ],
            "performance": [
                "When did you notice the slowness?",
                "Is it slow all the time or only when running specific programs?",
                "Did you recently install anything new?",
                "Have you restarted your computer recently?"
            ],
            "access": [
                "What are you trying to access?",
                "What error message do you see?",
                "Did your password change recently?",
                "Can you login to anything else (email, etc.)?"
            ]
        }
        
        # Get category-specific questions
        questions = templates.get(category, [
            "Can you provide more details about the issue?",
            "When did this problem start?",
            "Have you tried anything to fix it?"
        ])
        
        # If we already asked questions, ask follow-ups
        if conversation_history and len(conversation_history) > 2:
            return self._generate_followup_questions(description, conversation_history)
        
        return questions[:3]  # Max 3 questions at a time
    
    def _generate_followup_questions(
        self,
        description: str,
        conversation_history: List[Dict]
    ) -> List[str]:
        """Generate follow-up questions based on conversation."""
        
        # Build conversation context
        context = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation_history[-4:]  # Last 4 messages
        ])
        
        prompt = f"""Based on this IT support conversation, ask 1-2 follow-up questions to complete troubleshooting.

Conversation:
{context}

Current issue: {description}

Generate 1-2 specific follow-up questions to pinpoint the root cause.
Keep questions short and focused. Format as a simple list.
"""
        
        try:
            response = self.model.generate_content(prompt)
            # Parse questions
            questions = [
                line.strip('- ').strip()
                for line in response.text.split('\n')
                if line.strip() and not line.strip().startswith('#')
            ]
            return questions[:2]  # Max 2 follow-ups
            
        except Exception as e:
            logger.error(f"Follow-up question generation failed: {e}")
            return ["Can you try restarting and let me know if the issue persists?"]
    
    def generate_friendly_response(
        self,
        message: str,
        context: Dict = None
    ) -> str:
        """
        Generate a friendly, professional response.
        Makes the AI sound like a helpful IT technician.
        """
        
        user_name = context.get('user_name', 'there') if context else 'there'
        
        # Add personality
        greetings = {
            "first_contact": f"Hi {user_name}! I'm your IT support assistant. I'll help you get this sorted out.",
            "clarification": f"Thanks for those details, {user_name}. Let me ask a few more questions to pinpoint the issue.",
            "solution_found": f"Great news, {user_name}! I think I know what's causing this. Let me walk you through the fix.",
            "escalation": f"I understand this is frustrating, {user_name}. I'm going to escalate this to our specialist team who can help you faster."
        }
        
        return message
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        """
        Simple chat interface for general IT questions.
        
        Args:
            messages: List of {"role": "user/assistant", "content": "text"}
            temperature: Creativity level
        
        Returns:
            AI response text
        """
        try:
            # Get last user message
            last_msg = None
            for msg in reversed(messages):
                if msg["role"] == "user":
                    last_msg = msg["content"]
                    break
            
            if not last_msg:
                return "I didn't receive your message. Could you please try again?"
            
            # Generate response
            response = self.model.generate_content(
                last_msg,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=1000
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "I'm sorry, I encountered an error. Please try rephrasing your question or contact IT support directly."


# Singleton
_conversation_agent = None

def get_conversation_agent() -> ConversationAgent:
    """Get or create conversation agent."""
    global _conversation_agent
    if _conversation_agent is None:
        _conversation_agent = ConversationAgent()
    return _conversation_agent
