"""
Troubleshooter Agent - Provides step-by-step troubleshooting for system issues.
"""
import logging
from typing import Dict, Any, List
from langchain.prompts import ChatPromptTemplate
from app.config import get_settings
from app.services.rag_engine import get_rag_engine
from app.services.agents.tools import safe_tools
from app.core.llm_factory import get_chat_model

logger = logging.getLogger(__name__)
settings = get_settings()


class TroubleshooterAgent:
    """Agent for troubleshooting and resolving technical issues."""
    
    def __init__(self):
        """Initialize troubleshooter agent with LLM."""
        try:
            self.llm = get_chat_model(temperature=0.5)
            self.rag_engine = get_rag_engine()
            self.tools = safe_tools
            logger.info("Troubleshooter agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize troubleshooter agent: {e}")
            raise
    
    def generate_troubleshooting_steps(
        self,
        title: str,
        description: str,
        category: str
    ) -> List[str]:
        """
        Generate step-by-step troubleshooting instructions.
        """
        # Get relevant context from knowledge base
        query = f"{title}\n{description}"
        context = self.rag_engine.get_relevant_context(query, k=5)
        
        # Create troubleshooting prompt
        troubleshooting_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert IT troubleshooter. Generate clear, actionable troubleshooting steps.

Similar resolved tickets:
{context}

Based on the issue and past solutions, provide:
1. Immediate diagnostic steps
2. Common solutions to try
3. System checks to perform
4. Escalation criteria

Format as a numbered list of clear, actionable steps.
Keep steps concise and specific.
Include expected outcomes for each step.

Category: {category}"""),
            ("user", "Title: {title}\n\nDescription: {description}")
        ])
        
        try:
            chain = troubleshooting_prompt | self.llm
            response = chain.invoke({
                "title": title,
                "description": description,
                "context": context,
                "category": category
            })
            
            # Parse steps from response
            steps = self._parse_steps(response.content)
            return steps
            
        except Exception as e:
            logger.error(f"Error generating troubleshooting steps: {e}")
            return [
                "Check system logs for error messages",
                "Verify service status and connectivity",
                "Review recent changes or updates",
                "Contact technical support if issue persists"
            ]
    
    def _parse_steps(self, content: str) -> List[str]:
        """Parse numbered steps from LLM response."""
        lines = content.strip().split('\n')
        steps = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering and bullets
                step = line.lstrip('0123456789.-•) ').strip()
                if step:
                    steps.append(step)
        
        return steps if steps else [content]
    
    def run_diagnostics(self, issue_type: str) -> Dict[str, Any]:
        """
        Run automated diagnostics based on issue type.
        Uses safe mode tools to check system status.
        """
        diagnostics = {
            "timestamp": None,
            "checks_performed": [],
            "findings": []
        }
        
        # Determine what to check based on issue type
        if "database" in issue_type.lower() or "connection" in issue_type.lower():
            status = self.tools.check_system_status("database")
            diagnostics["checks_performed"].append("Database Status")
            diagnostics["findings"].append(status)
        
        if "network" in issue_type.lower() or "connectivity" in issue_type.lower():
            network = self.tools.check_network_connectivity()
            diagnostics["checks_performed"].append("Network Connectivity")
            diagnostics["findings"].append(network)
        
        if "disk" in issue_type.lower() or "storage" in issue_type.lower():
            disk = self.tools.check_disk_space()
            diagnostics["checks_performed"].append("Disk Space")
            diagnostics["findings"].append(disk)
        
        # Always check general system status
        if not diagnostics["checks_performed"]:
            status = self.tools.check_system_status("api_server")
            diagnostics["checks_performed"].append("General System Status")
            diagnostics["findings"].append(status)
        
        return diagnostics
    
    def suggest_resolution(
        self,
        title: str,
        description: str,
        diagnostics: Dict[str, Any]
    ) -> str:
        """
        Suggest a resolution based on the issue and diagnostic results.
        """
        resolution_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert IT support agent providing resolution recommendations.

Diagnostic Results:
{diagnostics}

Based on the issue description and diagnostic results, provide:
1. Root cause analysis
2. Recommended solution
3. Prevention steps

Be specific and actionable. If the issue cannot be fully resolved remotely, state what needs hands-on intervention."""),
            ("user", "Title: {title}\n\nDescription: {description}")
        ])
        
        try:
            chain = resolution_prompt | self.llm
            response = chain.invoke({
                "title": title,
                "description": description,
                "diagnostics": str(diagnostics)
            })
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating resolution: {e}")
            return "Unable to generate automatic resolution. Please escalate to technical support."
    
    def handle_issue(self, title: str, description: str, category: str) -> Dict[str, Any]:
        """
        Complete troubleshooting workflow: diagnose, troubleshoot, and suggest resolution.
        """
        # Run diagnostics
        diagnostics = self.run_diagnostics(description)
        
        # Generate troubleshooting steps
        steps = self.generate_troubleshooting_steps(title, description, category)
        
        # Suggest resolution
        resolution = self.suggest_resolution(title, description, diagnostics)
        
        return {
            "troubleshooting_steps": steps,
            "diagnostics": diagnostics,
            "suggested_resolution": resolution
        }


# Global troubleshooter agent instance
_troubleshooter_agent = None


def get_troubleshooter_agent() -> TroubleshooterAgent:
    """Get or create troubleshooter agent instance."""
    global _troubleshooter_agent
    if _troubleshooter_agent is None:
        _troubleshooter_agent = TroubleshooterAgent()
    return _troubleshooter_agent
