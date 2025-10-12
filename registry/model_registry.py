# registry/model_registry.py
from agents.inference_agent import InferenceAgent

def get_model_info():
    agent = InferenceAgent.get()
    return agent.get_info()
