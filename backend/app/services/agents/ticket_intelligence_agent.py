"""
Ticket Intelligence Agent - Analyzes conversations and manages tickets intelligently.

This agent:
1. Decides WHEN to create a ticket (not immediately, but after understanding the issue)
2. Analyzes conversation to determine priority (low/medium/high/critical)
3. Generates meaningful ticket titles and descriptions
4. Updates ticket status based on conversation progress
5. Detects urgency signals from user behavior

Best Practice: Separate concerns - this agent only handles ticket intelligence.
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TicketIntelligenceAgent:
    """
    Intelligent ticket management agent.
    Uses LLM to make smart decisions about tickets.
    """
    
    def __init__(self):
        """Initialize with Gemini LLM."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(
            settings.gemini_model,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,  # Lower temperature for analytical tasks
                max_output_tokens=300
            ),
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
            }
        )
        
        logger.info("Ticket Intelligence Agent initialized")
    
    def should_create_ticket(
        self, 
        conversation_history: List[Dict],
        turn_count: int
    ) -> Dict:
        """
        Analyze if we should create a ticket NOW.
        
        Don't create ticket on first message - wait until:
        - User has explained the issue clearly (2-3 turns)
        - Issue seems technical and not immediately resolvable
        - User is asking for help (not just chatting)
        
        Returns: {
            "should_create": bool,
            "reason": str
        }
        """
        # Don't create on first 2 turns - need context
        if turn_count < 3:
            return {
                "should_create": False,
                "reason": f"Need more context (turn {turn_count}/3)"
            }
        
        # Use rule-based logic instead of LLM (more reliable, no safety filter issues)
        # CRITICAL FIX: Only check RECENT messages for technical content
        # Users might mention casual things ("umbrella") before describing tech issues
        
        # Technical issue keywords
        tech_keywords = [
            'slow', 'crash', 'error', 'not working', 'problem', 'issue',
            'help', 'fix', 'broken', 'freeze', 'hang', 'wont', "can't", 'cant',
            'laptop', 'computer', 'phone', 'app', 'software', 'device',
            'network', 'wifi', 'internet', 'login', 'password', 'access'
        ]
        
        # Get ONLY recent user messages (last 5) to check for technical content
        recent_user_messages = [
            msg.get('content', '') 
            for msg in conversation_history 
            if msg['role'] == 'user'
        ][-5:]  # Last 5 user messages only
        
        recent_text = ' '.join(recent_user_messages).lower()
        
        # Check if recent messages contain technical issues
        has_tech = any(keyword in recent_text for keyword in tech_keywords)
        
        # Count substantial technical messages (not just "hi", "okay", "cant")
        substantial_tech_messages = [
            msg for msg in recent_user_messages
            if len(msg) > 15 and any(keyword in msg.lower() for keyword in tech_keywords)
        ]
        
        should_create = has_tech and len(substantial_tech_messages) >= 1
        
        if should_create:
            reason = f"Technical issue detected: {len(substantial_tech_messages)} detailed tech message(s) in recent conversation"
        elif not has_tech:
            reason = "No technical keywords in recent messages"
        else:
            reason = f"Not enough detail yet ({len(substantial_tech_messages)} substantial messages)"
        
        logger.info(f"[TICKET-AI] Create decision: {should_create} - {reason}")
        return {
            "should_create": should_create,
            "reason": reason
        }
    
    def analyze_priority(
        self,
        conversation_history: List[Dict],
        issue_description: str = ""
    ) -> Dict:
        """
        Analyze conversation to determine ticket priority.
        
        Priority levels:
        - CRITICAL: System down, blocking work for multiple users, security issue
        - HIGH: Blocking work for single user, urgent deadline, repeated escalation
        - MEDIUM: Impacting work but has workaround, general issues
        - LOW: Minor inconvenience, feature requests, questions
        
        Returns: {
            "priority": "critical|high|medium|low",
            "urgency_score": 0-10,
            "reason": str,
            "urgency_signals": [...]
        }
        """
        # Use rule-based priority detection (more reliable than LLM)
        conv_text = self._format_conversation(conversation_history).lower()
        
        urgency_signals = []
        urgency_score = 5  # Default medium
        
        # Critical signals (score: +4)
        critical_keywords = [
            'critical', 'emergency', 'system down', 'server down', 'completely down',
            'not working at all', 'everyone affected', 'security breach', 'entire team',
            'production down', 'site down'
        ]
        for keyword in critical_keywords:
            if keyword in conv_text:
                urgency_signals.append(keyword)
                urgency_score += 4
        
        # High urgency signals (score: +3)
        high_keywords = ['urgent', 'asap', 'deadline', 'meeting', 'presentation', "can't work", "cant work", 'blocking']
        for keyword in high_keywords:
            if keyword in conv_text:
                urgency_signals.append(keyword)
                urgency_score += 3
        
        # Frustration signals (score: +2)
        frustration_keywords = ['still not', 'nothing works', 'tried everything', 'not helping', 'frustrated']
        for keyword in frustration_keywords:
            if keyword in conv_text:
                urgency_signals.append('frustration: ' + keyword)
                urgency_score += 2
        
        # Time pressure (score: +3)
        # Check ONLY user messages for time pressure (not bot responses)
        user_text = ' '.join([m.get('content', '') for m in conversation_history if m['role'] == 'user']).lower()
        time_keywords = ['in 30 minutes', 'in 1 hour', 'in 2 hours', 'urgent deadline', 'need it today', 'asap']
        has_time_pressure = any(keyword in user_text for keyword in time_keywords)
        
        # More specific time pattern matching
        import re
        time_pattern_match = re.search(r'in \d+ (minute|hour)', user_text)
        
        if has_time_pressure or time_pattern_match:
            urgency_signals.append('time pressure')
            urgency_score += 3
        
        # Cap urgency score at 10
        urgency_score = min(urgency_score, 10)
        
        # Determine priority
        if urgency_score >= 9:
            priority = "critical"
            reason = "Critical urgency - immediate attention required"
        elif urgency_score >= 7:
            priority = "high"
            reason = "High urgency - user is blocked or has tight deadline"
        elif urgency_score >= 4:
            priority = "medium"
            reason = "Standard issue requiring investigation"
        else:
            priority = "low"
            reason = "Low priority - minor inconvenience"
        
        logger.info(f"[TICKET-AI] Priority: {priority} (urgency: {urgency_score}/10) - Signals: {urgency_signals}")
        return {
            "priority": priority,
            "urgency_score": urgency_score,
            "reason": reason,
            "urgency_signals": urgency_signals
        }
    
    def generate_ticket_metadata(
        self,
        conversation_history: List[Dict],
        rag_context: Optional[str] = None
    ) -> Dict:
        """
        Generate intelligent ticket title and description.
        
        Returns: {
            "title": "Clear, concise issue summary (50-80 chars)",
            "description": "Detailed description with context",
            "category": "hardware|software|network|access|other",
            "affected_systems": ["system1", "system2"]
        }
        """
        # Extract metadata from conversation using simple rules
        user_messages = [m.get('content', '') for m in conversation_history if m['role'] == 'user']
        
        # Technical keywords to identify actual issue messages
        tech_keywords = [
            'slow', 'crash', 'error', 'not working', 'problem', 'issue',
            'fix', 'broken', 'freeze', 'hang', 'wont', "can't", 'cant',
            'laptop', 'computer', 'phone', 'app', 'software'
        ]
        
        # Find the FIRST message that contains technical keywords (not just greetings)
        technical_messages = [
            msg for msg in user_messages 
            if len(msg) > 10 and any(keyword in msg.lower() for keyword in tech_keywords)
        ]
        
        if not technical_messages:
            issue_text = user_messages[-1] if user_messages else "Technical Issue"
        else:
            issue_text = technical_messages[0]  # First technical message = main issue
        
        # Extract systems/apps mentioned
        systems = []
        system_keywords = {
            'laptop': 'laptop', 'computer': 'computer', 'pc': 'PC',
            'iphone': 'iPhone', 'ipad': 'iPad', 'android': 'Android', 'phone': 'phone',
            'chrome': 'Chrome', 'edge': 'Edge', 'firefox': 'Firefox', 'browser': 'Browser',
            'outlook': 'Outlook', 'teams': 'Teams', 'word': 'Word', 'excel': 'Excel',
            'vs code': 'VS Code', 'visual studio': 'Visual Studio',
            'vpn': 'VPN', 'wifi': 'WiFi', 'network': 'Network',
            'printer': 'Printer'
        }
        
        conv_lower = ' '.join(user_messages).lower()
        for keyword, display_name in system_keywords.items():
            if keyword in conv_lower:
                systems.append(display_name)
        
        # Categorize
        category = "other"
        if any(word in conv_lower for word in ['laptop', 'computer', 'pc', 'hardware', 'printer']):
            category = "hardware"
        elif any(word in conv_lower for word in ['app', 'software', 'program', 'chrome', 'outlook', 'word']):
            category = "software"
        elif any(word in conv_lower for word in ['wifi', 'network', 'vpn', 'internet', 'connection']):
            category = "network"
        elif any(word in conv_lower for word in ['login', 'password', 'access', 'locked out']):
            category = "access"
        
        # Generate title
        title_templates = {
            'slow': '{system} performance degradation',
            'crash': '{system} crashing or freezing',
            'not working': '{system} not functioning properly',
            'error': '{system} showing error messages',
            'high cpu': '{system} excessive CPU usage',
            'vpn': 'VPN connection issues',
            'wifi': 'WiFi connectivity problems',
            'login': 'Unable to login or access system'
        }
        
        title = issue_text[:60]  # Default
        system_name = systems[0] if systems else "System"
        
        for keyword, template in title_templates.items():
            if keyword in conv_lower:
                title = template.format(system=system_name)
                break
        
        # Generate description (use ONLY technical messages, not casual chat)
        tech_keywords_check = [
            'slow', 'crash', 'error', 'not working', 'problem', 'issue',
            'fix', 'broken', 'freeze', 'hang', 'wont', "can't", 'cant',
            'laptop', 'computer', 'phone', 'app', 'software', 'meeting', 'urgent'
        ]
        
        technical_messages = [
            msg for msg in user_messages
            if any(keyword in msg.lower() for keyword in tech_keywords_check)
        ]
        
        description = f"Issue: {issue_text}\n"
        
        # Add ONLY technical details (skip greetings, umbrella, etc.)
        additional_tech_messages = [msg for msg in technical_messages[1:3] if msg != issue_text]
        if additional_tech_messages:
            description += f"\nAdditional details: {' | '.join(additional_tech_messages)}"
        
        description += f"\n\nAffected systems: {', '.join(systems) if systems else 'Not specified'}"
        description += f"\nCategory: {category}"
        description += f"\nStatus: Under investigation"
        
        logger.info(f"[TICKET-AI] Generated title: {title}")
        return {
            "title": title[:100],
            "description": description,
            "category": category,
            "affected_systems": systems
        }
    
    def should_update_priority(
        self,
        conversation_history: List[Dict],
        current_priority: str,
        turn_count: int
    ) -> Dict:
        """
        Detect if priority should be escalated based on:
        - User frustration increasing
        - Multiple failed attempts
        - Urgency signals appearing
        - User explicitly saying "urgent" or "critical"
        
        Returns: {
            "should_update": bool,
            "new_priority": str,
            "reason": str
        }
        """
        # Only check after a few turns
        if turn_count < 4:
            return {"should_update": False, "new_priority": current_priority, "reason": "Too early"}
        
        # Use rule-based escalation detection
        recent_messages = conversation_history[-6:]  # Last 6 messages
        recent_text = ' '.join([m.get('content', '') for m in recent_messages]).lower()
        
        # Re-analyze priority with recent messages
        recent_priority = self.analyze_priority(recent_messages, "")
        new_priority = recent_priority['priority']
        
        # Priority escalation mapping
        priority_order = ['low', 'medium', 'high', 'critical']
        current_index = priority_order.index(current_priority) if current_priority in priority_order else 1
        new_index = priority_order.index(new_priority)
        
        should_update = new_index > current_index
        
        if should_update:
            reason = f"Escalated due to: {', '.join(recent_priority['urgency_signals'][:3])}"
            logger.info(f"[TICKET-AI] Priority escalation: {current_priority} -> {new_priority} - {reason}")
            return {
                "should_update": True,
                "new_priority": new_priority,
                "reason": reason,
                "urgency_signals": recent_priority['urgency_signals']
            }
        else:
            return {
                "should_update": False,
                "new_priority": current_priority,
                "reason": "No escalation needed"
            }
    
    def detect_resolution(
        self,
        conversation_history: List[Dict]
    ) -> Dict:
        """
        Detect if issue is resolved based on conversation.
        
        Returns: {
            "is_resolved": bool,
            "confidence": 0-10,
            "resolution_summary": str
        }
        """
        # Check last 3 user messages for resolution signals
        recent_user_messages = [
            m.get('content', '') 
            for m in conversation_history[-6:] 
            if m['role'] == 'user'
        ][-3:]  # Last 3 user messages
        
        if not recent_user_messages:
            return {"is_resolved": False, "confidence": 0, "resolution_summary": "No user messages"}
        
        recent_text = ' '.join(recent_user_messages).lower()
        
        # Positive resolution signals
        resolved_keywords = [
            'fixed', 'working now', 'solved', 'resolved', 'perfect', 
            'that worked', 'thank you', 'thanks it', 'great that helped',
            'working perfectly', 'all good', 'problem solved'
        ]
        
        # Negative signals (not resolved)
        not_resolved_keywords = [
            'still', 'not working', 'same issue', 'nothing', 'cant', 
            'doesnt work', 'no', 'problem persists', 'still slow'
        ]
        
        # Count positive and negative signals
        positive_count = sum(1 for keyword in resolved_keywords if keyword in recent_text)
        negative_count = sum(1 for keyword in not_resolved_keywords if keyword in recent_text)
        
        # Determine resolution
        is_resolved = positive_count > 0 and negative_count == 0
        
        # Calculate confidence
        if is_resolved:
            confidence = min(7 + positive_count * 2, 10)  # 7-10 range
            summary = f"Issue resolved - user confirmed: {recent_user_messages[-1][:50]}"
        else:
            confidence = 0
            summary = "Still troubleshooting" if negative_count > 0 else "No clear resolution signal"
        
        if is_resolved:
            logger.info(f"[TICKET-AI] Issue resolved (confidence: {confidence}/10): {summary}")
        
        return {
            "is_resolved": is_resolved,
            "confidence": confidence,
            "resolution_summary": summary
        }
    
    # Helper methods for parsing LLM responses
    
    def _format_conversation(self, messages: List[Dict]) -> str:
        """Format conversation for LLM analysis."""
        formatted = []
        for msg in messages[-10:]:  # Last 10 messages max
            role = "User" if msg['role'] == 'user' else "Agent"
            content = msg.get('content', msg.get('parts', [''])[0] if 'parts' in msg else '')
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
    
    def _parse_decision(self, text: str) -> Dict:
        """Parse should_create_ticket response."""
        lines = text.strip().split('\n')
        should_create = False
        reason = "Unable to parse response"
        
        for line in lines:
            if line.startswith('CREATE:'):
                should_create = 'yes' in line.lower()
            elif line.startswith('REASON:'):
                reason = line.replace('REASON:', '').strip()
        
        return {"should_create": should_create, "reason": reason}
    
    def _parse_priority_analysis(self, text: str) -> Dict:
        """Parse analyze_priority response."""
        lines = text.strip().split('\n')
        priority = "medium"
        urgency = 5
        signals = []
        reason = ""
        
        for line in lines:
            if line.startswith('PRIORITY:'):
                priority = line.replace('PRIORITY:', '').strip().lower()
            elif line.startswith('URGENCY:'):
                try:
                    urgency = int(line.replace('URGENCY:', '').strip())
                except:
                    urgency = 5
            elif line.startswith('SIGNALS:'):
                signals = [s.strip() for s in line.replace('SIGNALS:', '').split(',')]
            elif line.startswith('REASON:'):
                reason = line.replace('REASON:', '').strip()
        
        return {
            "priority": priority,
            "urgency_score": urgency,
            "urgency_signals": signals,
            "reason": reason
        }
    
    def _parse_metadata(self, text: str) -> Dict:
        """Parse generate_ticket_metadata response."""
        lines = text.strip().split('\n')
        title = "Technical Issue"
        description = ""
        category = "other"
        affected = []
        
        for line in lines:
            if line.startswith('TITLE:'):
                title = line.replace('TITLE:', '').strip()
            elif line.startswith('DESCRIPTION:'):
                description = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('CATEGORY:'):
                category = line.replace('CATEGORY:', '').strip().lower()
            elif line.startswith('AFFECTED:'):
                affected = [s.strip() for s in line.replace('AFFECTED:', '').split(',') if s.strip()]
        
        return {
            "title": title[:100],  # Max 100 chars
            "description": description or title,
            "category": category,
            "affected_systems": affected
        }
    
    def _parse_update_decision(self, text: str, current: str) -> Dict:
        """Parse should_update_priority response."""
        lines = text.strip().split('\n')
        should_update = False
        new_priority = current
        reason = ""
        
        for line in lines:
            if line.startswith('UPDATE:'):
                should_update = 'yes' in line.lower()
            elif line.startswith('NEW_PRIORITY:'):
                new_priority = line.replace('NEW_PRIORITY:', '').strip().lower()
            elif line.startswith('REASON:'):
                reason = line.replace('REASON:', '').strip()
        
        return {
            "should_update": should_update,
            "new_priority": new_priority,
            "reason": reason
        }
    
    def _parse_resolution(self, text: str) -> Dict:
        """Parse detect_resolution response."""
        lines = text.strip().split('\n')
        is_resolved = False
        confidence = 0
        summary = ""
        
        for line in lines:
            if line.startswith('RESOLVED:'):
                is_resolved = 'yes' in line.lower()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = int(line.replace('CONFIDENCE:', '').strip())
                except:
                    confidence = 0
            elif line.startswith('SUMMARY:'):
                summary = line.replace('SUMMARY:', '').strip()
        
        return {
            "is_resolved": is_resolved,
            "confidence": confidence,
            "resolution_summary": summary
        }


# Global instance
_ticket_agent_instance = None

def get_ticket_intelligence_agent() -> TicketIntelligenceAgent:
    """Get or create the global ticket intelligence agent."""
    global _ticket_agent_instance
    if _ticket_agent_instance is None:
        _ticket_agent_instance = TicketIntelligenceAgent()
    return _ticket_agent_instance
