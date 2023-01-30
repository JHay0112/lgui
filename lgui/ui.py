"""
Defines the abstract interface for lcapy user interfaces
"""

from abc import ABC, abstractmethod

class UserInterface(ABC):
    """
    Abstract base class for user interfaces
    """
    
    @abstractmethod
    def display(self):
        ...