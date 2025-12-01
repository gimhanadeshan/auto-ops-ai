"""
Enhanced Multi-Turn Diagnostic Conversation Engine
Conducts intelligent troubleshooting conversations with context awareness,
temporal urgency detection, progressive diagnostic flows, and embedding-based
similarity matching.
"""
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import google.generativeai as genai
from app.config import get_settings
from app.models.conversation_state import (
    ConversationState, ConversationPhase, ConversationContext,
    DiagnosticQuestion, TroubleshootingStep, UrgencyLevel
)

logger = logging.getLogger(__name__)
settings = get_settings()


class EnhancedConversationAgent:
    """
    Advanced conversation agent with multi-turn diagnostics,
    urgency detection, and intelligent troubleshooting flows.
    """
    
    def __init__(self):
        """Initialize the enhanced conversation agent."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        # In-memory conversation state storage
        self.active_conversations: Dict[str, ConversationState] = {}
        
        logger.info("Enhanced Conversation Agent initialized")
    
    def get_or_create_conversation(self, user_email: str) -> ConversationState:
        """Get existing conversation or create new one."""
        if user_email not in self.active_conversations:
            conversation_id = f"{user_email}_{datetime.utcnow().timestamp()}"
            self.active_conversations[user_email] = ConversationState(
                conversation_id=conversation_id,
                user_email=user_email,
                context=ConversationContext()
            )
        return self.active_conversations[user_email]
    
    def reset_conversation(self, user_email: str):
        """Reset conversation for new issue."""
        if user_email in self.active_conversations:
            del self.active_conversations[user_email]
    
    def detect_urgency_indicators(self, message: str, state: ConversationState) -> UrgencyLevel:
        """Detect urgency from user message and update context."""
        indicators = []
        urgency = UrgencyLevel.LOW
        message_lower = message.lower()
        
        # Critical indicators
        critical_keywords = ["critical", "emergency", "urgent", "immediately", "asap", 
                            "down", "crashed", "can't work", "production", "security breach",
                            "data loss", "system down"]
        if any(keyword in message_lower for keyword in critical_keywords):
            urgency = UrgencyLevel.CRITICAL
            indicators.append("critical_keywords")
        
        # Meeting/deadline detection with time extraction
        meeting_patterns = [
            (r"meeting in (\d+) (minute|min)s?", "minutes"),
            (r"meeting in (\d+) (hour|hr)s?", "hours"),
            (r"presentation in (\d+) (minute|min)s?", "minutes"),
            (r"demo in (\d+) (minute|min)s?", "minutes"),
        ]
        
        for pattern, unit in meeting_patterns:
            match = re.search(pattern, message_lower)
            if match:
                time_value = int(match.group(1))
                
                if unit == "minutes":
                    state.context.has_upcoming_meeting = True
                    state.context.meeting_time_minutes = time_value
                    
                    if time_value <= 30:
                        urgency = UrgencyLevel.CRITICAL
                        indicators.append(f"meeting_in_{time_value}_min")
                    elif time_value <= 60:
                        urgency = max(urgency, UrgencyLevel.HIGH)
                        indicators.append(f"meeting_soon")
                elif unit == "hours" and time_value <= 2:
                    state.context.has_upcoming_meeting = True
                    state.context.meeting_time_minutes = time_value * 60
                    urgency = max(urgency, UrgencyLevel.HIGH)
                    indicators.append(f"meeting_today")
        
        # Blocking work indicators
        blocking_keywords = ["can't", "cannot", "unable", "blocking", "stuck", 
                            "won't", "doesn't work", "not working", "can not"]
        if any(keyword in message_lower for keyword in blocking_keywords):
            state.context.blocking_work = True
            urgency = max(urgency, UrgencyLevel.HIGH)
            indicators.append("blocking_work")
        
        # Data risk indicators
        data_keywords = ["lost data", "deleted", "missing files", "corrupted", 
                        "backup", "recovery", "can't access files"]
        if any(keyword in message_lower for keyword in data_keywords):
            state.context.data_at_risk = True
            urgency = UrgencyLevel.CRITICAL
            indicators.append("data_at_risk")
        
        # Multiple users affected
        multi_user = ["team", "everyone", "multiple people", "all users", "department", "whole office"]
        if any(keyword in message_lower for keyword in multi_user):
            state.context.affected_users_count = 10  # Estimate
            urgency = max(urgency, UrgencyLevel.HIGH)
            indicators.append("multiple_users")
        
        # Frustration indicators (escalate faster)
        frustration_keywords = ["again", "still", "already tried", "nothing works", 
                               "frustrated", "this is ridiculous"]
        frustration_count = sum(1 for kw in frustration_keywords if kw in message_lower)
        state.context.user_frustration_level = min(10, state.context.user_frustration_level + frustration_count)
        
        state.context.urgency_indicators = indicators
        return urgency
    
    def extract_temporal_context(self, message: str, state: ConversationState):
        """Extract when the issue occurred."""
        message_lower = message.lower()
        
        # Time of occurrence
        time_patterns = {
            "just now": "immediate",
            "right now": "immediate",
            "this morning": "today_morning",
            "this afternoon": "today_afternoon",
            "today": "today",
            "yesterday": "yesterday",
            "last week": "last_week",
            "few minutes ago": "recent",
            "an hour ago": "recent",
        }
        
        for pattern, value in time_patterns.items():
            if pattern in message_lower:
                state.context.time_of_occurrence = value
                break
        
        # Frequency
        frequency_patterns = {
            "first time": "first_occurrence",
            "keeps happening": "recurring",
            "always": "consistent",
            "sometimes": "intermittent",
            "every time": "consistent",
            "randomly": "intermittent",
            "happened before": "recurring"
        }
        
        for pattern, value in frequency_patterns.items():
            if pattern in message_lower:
                state.context.frequency = value
                break
    
    def extract_error_messages(self, message: str, state: ConversationState):
        """Extract error messages from user input."""
        # Look for quoted text or error codes
        quoted = re.findall(r'"([^"]*)"', message)
        error_codes = re.findall(r'error\s*(?:code)?\s*[:]*\s*(\w+[-_]?\d+)', message, re.IGNORECASE)
        
        errors = quoted + error_codes
        if errors:
            state.context.error_messages.extend(errors)
    
    def extract_steps_taken(self, message: str, state: ConversationState):
        """Extract what user already tried."""
        message_lower = message.lower()
        
        attempted_actions = {
            "restart": ["restart", "reboot", "rebooted", "turned off and on"],
            "update": ["update", "updated", "upgrade"],
            "reinstall": ["reinstall", "reinstalled", "uninstall"],
            "clear_cache": ["clear cache", "cleared cache", "delete cache"],
            "check_cables": ["check cable", "checked cables", "plugged in"],
            "reset_password": ["reset password", "changed password"],
        }
        
        for action, keywords in attempted_actions.items():
            if any(kw in message_lower for kw in keywords):
                if action not in state.context.steps_already_taken:
                    state.context.steps_already_taken.append(action)
    
    def categorize_issue(self, description: str) -> str:
        """Categorize issue by keywords."""
        desc_lower = description.lower()
        
        categories = {
            "network": ["vpn", "network", "wifi", "internet", "connection", "connectivity", "dns"],
            "hardware": ["bsod", "blue screen", "crash", "hardware", "monitor", "keyboard", "mouse", "laptop"],
            "performance": ["slow", "freeze", "hang", "performance", "lag", "takes forever"],
            "access": ["login", "password", "access", "permission", "denied", "locked out"],
            "software": ["outlook", "teams", "chrome", "excel", "word", "software", "app", "application"],
            "email": ["email", "outlook", "send mail", "receive mail", "inbox"],
            "printer": ["print", "printer", "printing", "print job"]
        }
        
        for category, keywords in categories.items():
            if any(kw in desc_lower for kw in keywords):
                return category
        
        return "other"
    
    def generate_diagnostic_questions(self, state: ConversationState) -> List[DiagnosticQuestion]:
        """Generate context-aware diagnostic questions."""
        questions = []
        context = state.context
        category = context.category or "other"
        
        # Time questions (if not answered)
        if not context.time_of_occurrence:
            questions.append(DiagnosticQuestion(
                question="When did this issue start? (just now, this morning, yesterday, etc.)",
                question_type="time",
                expected_info="time_of_occurrence",
                priority=1
            ))
        
        # Frequency questions
        if not context.frequency:
            questions.append(DiagnosticQuestion(
                question="Is this the first time this happened, or does it keep occurring?",
                question_type="frequency",
                expected_info="frequency",
                priority=2
            ))
        
        # Error messages
        if not context.error_messages:
            questions.append(DiagnosticQuestion(
                question="Are you seeing any error messages? If yes, what does it say?",
                question_type="error_details",
                expected_info="error_messages",
                priority=1
            ))
        
        # Category-specific questions
        category_questions = {
            "network": [
                "Are you on WiFi or wired ethernet?",
                "Can you access other websites or just specific ones?",
            ],
            "hardware": [
                "Does it happen all the time or only sometimes?",
                "Did you recently drop or move the device?",
            ],
            "software": [
                "Which specific program is having the issue?",
                "Did you recently install any updates?",
            ],
            "performance": [
                "Is it slow all the time or only with certain programs?",
                "How long has it been since you restarted your computer?",
            ],
            "access": [
                "What are you trying to access?",
                "Did your password expire or change recently?",
            ]
        }
        
        if category in category_questions:
            for q in category_questions[category]:
                questions.append(DiagnosticQuestion(
                    question=q,
                    question_type="category_specific",
                    expected_info=f"{category}_details",
                    priority=3
                ))
        
        # Sort by priority and return top 2
        questions.sort(key=lambda x: x.priority)
        return questions[:2]
    
    def generate_troubleshooting_steps(self, state: ConversationState, similar_issues: List[Dict] = None) -> List[TroubleshootingStep]:
        """Generate progressive troubleshooting steps from KB or predefined flows."""
        category = state.context.category or "other"
        already_tried = state.context.steps_already_taken
        
        # Priority 1: Use steps from similar resolved issues (from dataset analyzer)
        if similar_issues and len(similar_issues) > 0:
            kb_steps = []
            for i, similar in enumerate(similar_issues[:1]):  # Use top match
                if 'resolution_steps' in similar:
                    for step_num, step_text in enumerate(similar['resolution_steps'], 1):
                        kb_steps.append(TroubleshootingStep(
                            step_number=step_num,
                            instruction=step_text,
                            expected_outcome="Issue resolved",
                            success_indicators=["worked", "fixed", "resolved", "yes", "success"],
                            failure_indicators=["no", "still", "didn't work", "same problem"],
                            estimated_time="2-3 minutes",
                            difficulty="medium",
                            requires_restart="restart" in step_text.lower()
                        ))
            
            if kb_steps:
                logger.info(f"Using {len(kb_steps)} steps from KB article (similarity: {similar_issues[0].get('similarity_score', 0)})")
                return kb_steps
        
        # Category-specific troubleshooting flows
        troubleshooting_flows = {
            "network": [
                TroubleshootingStep(
                    step_number=1,
                    instruction="Let's start simple: Can you disconnect and reconnect to the WiFi network? Click the WiFi icon and select your network again.",
                    expected_outcome="WiFi reconnects successfully",
                    success_indicators=["connected", "working", "fixed", "yes"],
                    failure_indicators=["no", "still", "same", "didn't work"],
                    estimated_time="30 seconds",
                    difficulty="easy",
                    requires_restart=False
                ),
                TroubleshootingStep(
                    step_number=2,
                    instruction="Let's try flushing the DNS cache. Open Command Prompt and type: ipconfig /flushdns",
                    expected_outcome="DNS cache cleared",
                    success_indicators=["worked", "connected", "fixed"],
                    failure_indicators=["no", "still", "error"],
                    estimated_time="1 minute",
                    difficulty="easy",
                    requires_restart=False
                ),
                TroubleshootingStep(
                    step_number=3,
                    instruction="Let's restart your computer to refresh network settings. Save your work first, then restart.",
                    expected_outcome="Network connectivity restored after restart",
                    success_indicators=["working", "fixed", "connected"],
                    failure_indicators=["no", "still not working"],
                    estimated_time="3 minutes",
                    difficulty="easy",
                    requires_restart=True
                ),
            ],
            "performance": [
                TroubleshootingStep(
                    step_number=1,
                    instruction="Let's check what's using resources. Press Ctrl+Shift+Esc to open Task Manager. Click 'More details' if needed. What's using the most CPU or Memory?",
                    expected_outcome="Identified resource-heavy process",
                    success_indicators=["see", "found", "shows"],
                    failure_indicators=["nothing", "normal", "don't see"],
                    estimated_time="1 minute",
                    difficulty="easy",
                    requires_restart=False
                ),
                TroubleshootingStep(
                    step_number=2,
                    instruction="Close any unnecessary programs, especially browser tabs. Then let's restart your computer to clear memory.",
                    expected_outcome="Performance improves after restart",
                    success_indicators=["faster", "better", "fixed", "working"],
                    failure_indicators=["still slow", "same", "no change"],
                    estimated_time="3 minutes",
                    difficulty="easy",
                    requires_restart=True
                ),
            ],
            "access": [
                TroubleshootingStep(
                    step_number=1,
                    instruction="Let's verify your credentials. Try logging out completely and logging back in. Make sure Caps Lock is off.",
                    expected_outcome="Successfully logged in",
                    success_indicators=["logged in", "worked", "success"],
                    failure_indicators=["still can't", "denied", "error"],
                    estimated_time="1 minute",
                    difficulty="easy",
                    requires_restart=False
                ),
                TroubleshootingStep(
                    step_number=2,
                    instruction="Your password might need resetting. I'll escalate this to get your password reset by IT staff.",
                    expected_outcome="Password reset initiated",
                    success_indicators=["okay", "yes", "please"],
                    failure_indicators=["no"],
                    estimated_time="5 minutes",
                    difficulty="medium",
                    requires_restart=False
                ),
            ],
        }
        
        # Get steps for category (or generic steps)
        steps = troubleshooting_flows.get(category, [
            TroubleshootingStep(
                step_number=1,
                instruction="Let's start by restarting your computer. This often resolves many issues. Please save your work and restart.",
                expected_outcome="Issue resolved after restart",
                success_indicators=["fixed", "working", "resolved"],
                failure_indicators=["still", "no", "same"],
                estimated_time="3 minutes",
                difficulty="easy",
                requires_restart=True
            ),
        ])
        
        # Filter out already attempted steps
        filtered_steps = []
        for step in steps:
            step_keywords = step.instruction.lower()
            should_skip = False
            
            for attempted in already_tried:
                if attempted in step_keywords or attempted.replace("_", " ") in step_keywords:
                    should_skip = True
                    break
            
            if not should_skip:
                filtered_steps.append(step)
        
        return filtered_steps
    
    def should_escalate_to_human(self, state: ConversationState) -> Tuple[bool, List[str]]:
        """Decide if issue should be escalated to human IT staff."""
        reasons = []
        
        # Critical issues always escalate
        if state.context.data_at_risk:
            reasons.append("Data loss risk detected - requires immediate specialist attention")
        
        # Security issues
        security_keywords = ["hack", "breach", "security", "virus", "malware", "ransomware"]
        if any(kw in state.context.issue_description.lower() for kw in security_keywords):
            reasons.append("Security-related issue - requires specialist review")
        
        # Too many failed troubleshooting attempts
        failed_attempts = len(state.context.attempted_solutions)
        if failed_attempts >= 3:
            reasons.append(f"Multiple troubleshooting attempts ({failed_attempts}) have not resolved the issue")
        
        # High frustration level
        if state.context.user_frustration_level >= 5:
            reasons.append("User experiencing high frustration - human touch needed")
        
        # Critical urgency with meeting
        if state.context.has_upcoming_meeting and state.context.meeting_time_minutes and state.context.meeting_time_minutes <= 15:
            reasons.append(f"Critical: User has meeting in {state.context.meeting_time_minutes} minutes")
        
        # Multiple users affected
        if state.context.affected_users_count > 5:
            reasons.append(f"Widespread issue affecting {state.context.affected_users_count}+ users")
        
        # Hardware issues often need physical inspection
        if state.context.category == "hardware" and failed_attempts >= 1:
            reasons.append("Hardware issue may require physical inspection")
        
        return len(reasons) > 0, reasons
    
    def process_user_response(self, user_message: str, state: ConversationState) -> Dict:
        """
        Process user message and advance conversation state.
        Returns next action and response.
        """
        state.turn_count += 1
        state.last_updated = datetime.utcnow()
        
        # Extract all context from message
        self.detect_urgency_indicators(user_message, state)
        self.extract_temporal_context(user_message, state)
        self.extract_error_messages(user_message, state)
        self.extract_steps_taken(user_message, state)
        
        # State machine logic
        if state.phase == ConversationPhase.GREETING:
            return self._handle_greeting(user_message, state)
        
        elif state.phase == ConversationPhase.ISSUE_GATHERING:
            return self._handle_issue_gathering(user_message, state)
        
        elif state.phase == ConversationPhase.DIAGNOSTICS:
            return self._handle_diagnostics(user_message, state)
        
        elif state.phase == ConversationPhase.TROUBLESHOOTING:
            return self._handle_troubleshooting(user_message, state)
        
        elif state.phase == ConversationPhase.MONITORING:
            return self._handle_monitoring(user_message, state)
        
        return {"action": "error", "message": "Unknown conversation state"}
    
    def _handle_greeting(self, message: str, state: ConversationState) -> Dict:
        """Handle initial greeting phase."""
        message_lower = message.lower().strip()
        
        # Check if it's just a greeting or has issue info
        greeting_only = any(message_lower == g for g in ["hi", "hello", "hey", "help"])
        
        if greeting_only:
            return {
                "action": "greet",
                "message": "👋 Hi! I'm your IT Support Assistant. I'm here to help troubleshoot and fix your IT issues. What problem are you experiencing today?",
                "phase": "greeting"
            }
        else:
            # User provided issue immediately, move to gathering
            state.context.issue_description = message
            state.context.category = self.categorize_issue(message)
            state.phase = ConversationPhase.ISSUE_GATHERING
            
            # Generate diagnostic questions
            questions = self.generate_diagnostic_questions(state)
            
            question_text = "\n".join([f"- {q.question}" for q in questions[:2]])
            
            return {
                "action": "gather_info",
                "message": f"I understand you're having issues with **{state.context.category}**. Let me ask a few questions to help diagnose this:\n\n{question_text}",
                "phase": "issue_gathering",
                "questions": questions
            }
    
    def _handle_issue_gathering(self, message: str, state: ConversationState) -> Dict:
        """Handle diagnostic information gathering."""
        # Update issue description
        if not state.context.issue_description:
            state.context.issue_description = message
            state.context.category = self.categorize_issue(message)
        
        # Track questions asked
        state.context.questions_asked.append(message)
        
        # Check if we have enough info to start troubleshooting
        # After 2 rounds of questions OR if we have key info, move to troubleshooting
        has_time = bool(state.context.time_of_occurrence)
        has_frequency = bool(state.context.frequency)
        has_category = bool(state.context.category)
        questions_asked_count = len(state.context.questions_asked)
        
        # Move to troubleshooting if: 
        # 1. We have all key info, OR
        # 2. We've asked 2+ questions (don't loop forever)
        should_start_troubleshooting = (has_time and has_frequency and has_category) or questions_asked_count >= 2
        
        if should_start_troubleshooting:
            # Move to troubleshooting
            state.phase = ConversationPhase.TROUBLESHOOTING
            
            # Generate troubleshooting steps
            steps = self.generate_troubleshooting_steps(state)
            
            if steps:
                first_step = steps[0]
                state.context.attempted_solutions.append({
                    "step": first_step.step_number,
                    "instruction": first_step.instruction,
                    "status": "in_progress"
                })
                
                return {
                    "action": "troubleshoot",
                    "message": f"Thanks for the information! Now let's try to fix this. 🔧\n\n**Step {first_step.step_number}**: {first_step.instruction}\n\n⏱️ This should take about {first_step.estimated_time}.\n\nLet me know what happens!",
                    "phase": "troubleshooting",
                    "step": first_step
                }
            else:
                # No specific steps, move to escalation
                state.phase = ConversationPhase.ESCALATION
                state.should_escalate = True
                state.escalation_reasons.append("No automated troubleshooting steps available for this issue")
                
                return {
                    "action": "escalate",
                    "message": "Thanks for the details. This issue requires hands-on assistance from our IT team. I'm creating a ticket with all the information you've provided, and a technician will reach out to you shortly.",
                    "phase": "escalation",
                    "create_ticket": True,
                    "ticket_priority": "medium"
                }
        
        # Need more info - ask more questions (but only if we haven't asked too many)
        if questions_asked_count < 2:
            questions = self.generate_diagnostic_questions(state)
            
            if questions:
                question_text = "\n".join([f"- {q.question}" for q in questions[:2]])
                
                return {
                    "action": "gather_more",
                    "message": f"Thanks for that information. A couple more questions:\n\n{question_text}",
                    "phase": "issue_gathering",
                    "questions": questions
                }
        
        # Fallback: move to troubleshooting anyway
        state.phase = ConversationPhase.TROUBLESHOOTING
        return self._handle_troubleshooting(message, state)
    
    def _handle_troubleshooting(self, message: str, state: ConversationState) -> Dict:
        """Handle troubleshooting phase."""
        message_lower = message.lower()
        
        # Check if current step succeeded
        current_solution = state.context.attempted_solutions[-1] if state.context.attempted_solutions else None
        
        if current_solution:
            # Get the step details
            steps = self.generate_troubleshooting_steps(state)
            current_step_num = current_solution["step"]
            current_step = next((s for s in steps if s.step_number == current_step_num), None)
            
            if current_step:
                # Check for success indicators
                success = any(indicator in message_lower for indicator in current_step.success_indicators)
                failure = any(indicator in message_lower for indicator in current_step.failure_indicators)
                
                if success:
                    # Problem solved!
                    state.phase = ConversationPhase.RESOLUTION
                    state.resolved = True
                    
                    return {
                        "action": "resolved",
                        "message": "🎉 Excellent! I'm glad that fixed the issue. Is there anything else I can help you with?",
                        "phase": "resolution",
                        "create_ticket": True,
                        "ticket_status": "resolved"
                    }
                
                elif failure:
                    # Step didn't work, try next
                    current_solution["status"] = "failed"
                    state.context.solution_feedback.append(message)
                    
                    # Check if we should escalate
                    should_escalate, reasons = self.should_escalate_to_human(state)
                    
                    if should_escalate:
                        state.phase = ConversationPhase.ESCALATION
                        state.should_escalate = True
                        state.escalation_reasons = reasons
                        
                        reasons_text = "\n".join([f"• {r}" for r in reasons])
                        
                        return {
                            "action": "escalate",
                            "message": f"I understand this is frustrating. Based on what we've tried, I'm escalating this to our specialist IT team:\n\n{reasons_text}\n\nThey'll reach out to you shortly with priority assistance. I'm creating a detailed ticket with everything we've discussed.",
                            "phase": "escalation",
                            "create_ticket": True,
                            "ticket_priority": "high" if "Critical" in reasons_text else "medium"
                        }
                    
                    # Try next step
                    next_step_index = len([s for s in state.context.attempted_solutions if s["status"] == "failed"])
                    
                    if next_step_index < len(steps):
                        next_step = steps[next_step_index]
                        state.context.attempted_solutions.append({
                            "step": next_step.step_number,
                            "instruction": next_step.instruction,
                            "status": "in_progress"
                        })
                        
                        return {
                            "action": "troubleshoot",
                            "message": f"No worries, let's try something else. 🔧\n\n**Step {next_step.step_number}**: {next_step.instruction}\n\n⏱️ Estimated time: {next_step.estimated_time}",
                            "phase": "troubleshooting",
                            "step": next_step
                        }
        
        # Default: ask for clarification
        return {
            "action": "clarify",
            "message": "Did that step help resolve the issue, or is the problem still occurring?",
            "phase": "troubleshooting"
        }
    
    def _handle_monitoring(self, message: str, state: ConversationState) -> Dict:
        """Handle monitoring after attempted fix."""
        message_lower = message.lower()
        
        positive_indicators = ["yes", "working", "fixed", "good", "better", "resolved"]
        negative_indicators = ["no", "still", "not working", "same", "worse"]
        
        if any(ind in message_lower for ind in positive_indicators):
            state.phase = ConversationPhase.RESOLUTION
            state.resolved = True
            
            return {
                "action": "resolved",
                "message": "🎉 Perfect! I'm glad we got that sorted out. I'll close this ticket as resolved. Feel free to reach out if you need anything else!",
                "phase": "resolution",
                "create_ticket": True,
                "ticket_status": "resolved"
            }
        elif any(ind in message_lower for ind in negative_indicators):
            # Back to troubleshooting
            state.phase = ConversationPhase.TROUBLESHOOTING
            return self._handle_troubleshooting(message, state)
        
        return {
            "action": "monitor",
            "message": "Is the issue resolved now, or are you still experiencing problems?",
            "phase": "monitoring"
        }
    
    def chat(self, messages: List[Dict], user_email: str) -> str:
        """Simple fallback chat method."""
        try:
            last_msg = next((msg["content"] for msg in reversed(messages) if msg["role"] == "user"), "")
            
            response = self.model.generate_content(
                f"You are a helpful IT support assistant. Respond to: {last_msg}",
                generation_config=genai.types.GenerationConfig(temperature=0.7, max_output_tokens=500)
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "I'm here to help with IT issues. Could you describe the problem you're experiencing?"


# Singleton instance
_enhanced_agent = None

def get_enhanced_conversation_agent() -> EnhancedConversationAgent:
    """Get or create enhanced conversation agent."""
    global _enhanced_agent
    if _enhanced_agent is None:
        _enhanced_agent = EnhancedConversationAgent()
    return _enhanced_agent
