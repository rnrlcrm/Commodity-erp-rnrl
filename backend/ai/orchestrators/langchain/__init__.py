"""
LangChain AI Orchestration

Integrates LangChain for AI workflows in the ERP system.

Exports:
- LangChainOrchestrator: Main orchestrator
- ConversationChain: Conversational AI
- AgentExecutor: AI agents with tools
- MemoryManager: Conversation memory
"""

from backend.ai.orchestrators.langchain.orchestrator import LangChainOrchestrator
from backend.ai.orchestrators.langchain.chains import ConversationChain
from backend.ai.orchestrators.langchain.agents import ERPAgent, TradeAssistant, ContractAssistant, QualityAssistant

__all__ = [
    "LangChainOrchestrator",
    "ConversationChain",
    "ERPAgent",
    "TradeAssistant",
    "ContractAssistant",
    "QualityAssistant",
    "AnalysisChain",
    "AgentExecutor",
    "ERPAgent",
    "MemoryManager",
]
