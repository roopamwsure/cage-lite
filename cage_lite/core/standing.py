from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentStanding:
    agent_id: str
    allowed_actions: set[str] = field(default_factory=set)
    max_payment_amount: Optional[float] = None
    active: bool = True

    def can_perform(self, action_type: str) -> bool:
        return self.active and action_type in self.allowed_actions