from abc import ABC, abstractmethod

class AgentClient(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def generate_action(user_input: str) -> dict:
        pass
    
    @abstractmethod
    def read_file(user_input: str, file_path: str) -> None:
        pass