import os
import json
from typing import List, Dict
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from radar.src.schemas import TopicBase, ExtractedTopics

class KeywordExtractor:
    def __init__(self):
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model_name = os.getenv("EXTRACTION_MODEL", "gemma4:latest")
        self.llm = ChatOllama(base_url=base_url, model=model_name, format="json")
        self.structured_llm = self.llm.with_structured_output(ExtractedTopics)

    async def extract_keywords(self, content: str) -> List[TopicBase]:
        system_prompt = """
        You are a keyword extraction specialist for the Attention Defense System.
        Extract relevant topics from the message content. 
        Categories: Project, Ticket, Office, Working Group, Individual.
        Return a JSON object with a list of 'topics', each having 'name' and 'category'.
        Example: {"topics": [{"name": "Project Alpha", "category": "Project"}, {"name": "TICKET-123", "category": "Ticket"}]}
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Extract topics from: {content}")
        ]
        
        try:
            result = await self.structured_llm.ainvoke(messages)
            if isinstance(result, ExtractedTopics):
                return result.topics
            return []
        except Exception as e:
            print(f"Error in structured extraction: {e}")
            return []

extractor = KeywordExtractor()
