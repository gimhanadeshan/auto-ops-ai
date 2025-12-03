"""
LLM-First Conversation Agent - Simple & Intelligent
The LLM is the brain. No hard-coded logic, just smart prompting.
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMConversationAgent:
    """
    Pure LLM-driven conversation agent.
    The LLM handles all conversation logic, classification, and response generation.
    """
    
    def __init__(self):
        """Initialize with Gemini LLM."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(
            settings.gemini_model,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,  # Creative but consistent
                max_output_tokens=500
            ),
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
            }
        )
        
        # Simple conversation memory: {user_email: [messages]}
        self.conversations: Dict[str, List[Dict]] = {}
        
        logger.info("LLM Conversation Agent initialized")
    
    def get_system_prompt(self, rag_context: Optional[str] = None) -> str:
        """
        The brain of the system - comprehensive system prompt.
        This tells the LLM EVERYTHING it needs to know.
        """
        prompt = """You are an intelligent IT Support Assistant. You help users troubleshoot technical issues through natural conversation.

## Your Capabilities:
1. **Support all devices** - Computers, laptops, phones (iPhone/Android), tablets, printers, etc.
2. **Understand user issues** - Ask clarifying questions if needed
3. **Check knowledge base** - Similar past issues will be provided to you
4. **Troubleshoot intelligently** - Suggest concrete, actionable steps
5. **Know when to escalate** - If you can't solve it, escalate to human IT team
6. **Handle non-technical chat** - Be friendly and helpful even for general questions

## Conversation Flow:
1. User describes issue → You ask clarifying questions if needed
2. You check if similar issues exist in knowledge base (provided below)
3. You suggest troubleshooting steps one at a time
4. User tries step and reports back → You adapt based on feedback
5. If solved → Celebrate! If not after 3 attempts → Escalate to human

## Response Format:
Your response should be natural and conversational. Examples:

**Good responses:**
- "I can help! Let's start by checking Task Manager. Press Ctrl+Shift+Esc and tell me what's using the most CPU."
- "For iPhone slowness, let's try clearing Safari cache first. Go to Settings > Safari > Clear History and Website Data."
- "Based on similar issues, this usually happens when Chrome has too many tabs. Try closing some tabs and let me know if it improves."
- "I've tried a few approaches but this seems persistent. I'm escalating this to our specialist team who can investigate deeper."

**Avoid:**
- Robotic templates like "Did that help? Yes/No"
- Asking the same question repeatedly
- Giving multiple steps at once (ONE step at a time!)

"""
        
        if rag_context:
            prompt += f"\n## Knowledge Base - Similar Past Issues:\n{rag_context}\n"
        
        prompt += """
## Current Conversation:
(Previous messages are shown below. Respond naturally to continue the conversation)

Remember: Be helpful, concise, and human-like. One clear step at a time!
"""
        
        return prompt
    
    def add_message(self, user_email: str, role: str, content: str):
        """Add message to conversation history."""
        if user_email not in self.conversations:
            self.conversations[user_email] = []
        
        self.conversations[user_email].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep last 20 messages to avoid context overflow
        if len(self.conversations[user_email]) > 20:
            self.conversations[user_email] = self.conversations[user_email][-20:]
    
    def build_conversation_context(self, user_email: str) -> List:
        """Build conversation context for LLM."""
        messages = self.conversations.get(user_email, [])
        
        # Format for Gemini
        context = []
        for msg in messages:
            context.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]]
            })
        
        return context
    
    def process_message(
        self, 
        user_email: str, 
        user_message: str, 
        rag_context: Optional[str] = None
    ) -> Dict:
        """
        Process user message and generate response.
        This is the ONLY method you need!
        
        Args:
            user_email: User identifier
            user_message: User's message
            rag_context: Similar issues from knowledge base (optional)
        
        Returns:
            {
                "message": "Bot response",
                "is_technical": bool,
                "should_escalate": bool,
                "metadata": {...}
            }
        """
        try:
            # Add user message to history
            self.add_message(user_email, "user", user_message)
            
            # Build conversation context
            system_prompt = self.get_system_prompt(rag_context)
            conversation = self.build_conversation_context(user_email)
            
            # Call LLM with full context
            logger.info(f"[LLM] Processing message for {user_email}: {user_message[:50]}...")
            if rag_context:
                logger.info(f"[LLM] RAG Context provided: {len(rag_context)} chars")
            logger.info(f"[LLM] Conversation history: {len(conversation)} messages")
            
            # Build prompt
            full_prompt = f"{system_prompt}\n\n"
            for msg in conversation[-5:]:  # Last 5 messages for context
                role = "User" if msg["role"] == "user" else "Assistant"
                full_prompt += f"{role}: {msg['parts'][0]}\n"
            
            full_prompt += "\nAssistant:"
            
            # Try to generate response
            response = self.model.generate_content(full_prompt)
            
            # Check if response was blocked by safety filters
            if not response or not response.text:
                logger.warning("[LLM] Empty response or safety filter block")
                
                # Try with simpler prompt (without RAG context that might trigger filters)
                if rag_context:
                    logger.info("[LLM] Retrying without RAG context...")
                    simple_prompt = self.get_system_prompt(None) + "\n\n"
                    for msg in conversation[-5:]:
                        role = "User" if msg["role"] == "user" else "Assistant"
                        simple_prompt += f"{role}: {msg['parts'][0]}\n"
                    simple_prompt += "\nAssistant:"
                    
                    response = self.model.generate_content(simple_prompt)
                    
                if not response or not response.text:
                    logger.warning("[LLM] Still blocked, using generic fallback")
                    bot_response = "I'm having trouble processing that. Could you rephrase what you need help with?"
                else:
                    bot_response = response.text.strip()
            else:
                bot_response = response.text.strip()
            
            # Add bot response to history
            self.add_message(user_email, "assistant", bot_response)
            
            logger.info(f"[LLM] Response generated: {bot_response[:100]}...")
            
            # Simple analysis of bot's own response to extract metadata
            is_technical = self._is_technical_conversation(conversation)
            should_escalate = any(word in bot_response.lower() for word in ["escalat", "specialist team", "human support"])
            is_resolved = any(word in bot_response.lower() for word in ["solved", "fixed", "resolved", "glad that helped"])
            
            return {
                "message": bot_response,
                "is_technical": is_technical,
                "should_escalate": should_escalate,
                "is_resolved": is_resolved,
                "metadata": {
                    "turn_count": len(conversation) // 2,
                    "rag_used": bool(rag_context)
                }
            }
            
        except Exception as e:
            logger.error(f"[LLM] Error processing message: {e}")
            return {
                "message": "I encountered an issue. Let me connect you with our support team who can help you better.",
                "is_technical": False,
                "should_escalate": True,
                "is_resolved": False,
                "metadata": {"error": str(e)}
            }
    
    def _is_technical_conversation(self, conversation: List) -> bool:
        """Simple heuristic to detect if conversation is technical."""
        if not conversation:
            return False
        
        # Check ALL user messages for IT keywords (not just first one)
        tech_keywords = [
            "computer", "laptop", "slow", "crash", "error", "wifi", "network",
            "software", "app", "application", "login", "password", "printer",
            "outlook", "email", "teams", "chrome", "browser", "windows", "mac",
            "cpu", "memory", "disk", "task manager", "vs code", "edge", "freeze"
        ]
        
        # Check any user message for technical keywords
        for msg in conversation:
            if msg["role"] == "user":
                content = msg["parts"][0].lower()
                if any(kw in content for kw in tech_keywords):
                    return True
        
        return False
    
    def reset_conversation(self, user_email: str):
        """Clear conversation history."""
        if user_email in self.conversations:
            del self.conversations[user_email]
            logger.info(f"[LLM] Reset conversation for {user_email}")


# Global instance
_agent_instance = None

def get_llm_conversation_agent() -> LLMConversationAgent:
    """Get or create the global LLM agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = LLMConversationAgent()
    return _agent_instance
