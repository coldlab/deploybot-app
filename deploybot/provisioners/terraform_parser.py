import re
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class ResourceEventType(Enum):
    CREATING = "creating"
    CREATED = "created"
    MODIFYING = "modifying"
    MODIFIED = "modified"
    DESTROYING = "destroying"
    DESTROYED = "destroyed"


@dataclass
class ResourceEvent:
    """Represents a resource event from Terraform output."""
    event_type: ResourceEventType
    resource_name: str
    duration: Optional[str] = None
    raw_line: str = ""


class TerraformOutputParser:
    """Parses Terraform output to extract resource events and format them nicely."""
    
    def __init__(self):
        # Patterns to match different Terraform output events
        self.patterns = {
            ResourceEventType.CREATING: r'(\w+\.\w+):\s*Creating\.\.\.',
            ResourceEventType.CREATED: r'(\w+\.\w+):\s*Creation complete after (\d+[ms])',
            ResourceEventType.MODIFYING: r'(\w+\.\w+):\s*Modifying\.\.\.',
            ResourceEventType.MODIFIED: r'(\w+\.\w+):\s*Modifications complete after (\d+[ms])',
            ResourceEventType.DESTROYING: r'(\w+\.\w+):\s*Destroying\.\.\.',
            ResourceEventType.DESTROYED: r'(\w+\.\w+):\s*Destruction complete after (\d+[ms])',
        }
    
    def parse_line(self, line: str) -> Optional[ResourceEvent]:
        """Parse a single line of Terraform output."""
        line = line.strip()
        if not line:
            return None
            
        for event_type, pattern in self.patterns.items():
            match = re.search(pattern, line)
            if match:
                full_name = match.group(1)
                resource_name = self._extract_resource_name(full_name)
                duration = match.group(2) if len(match.groups()) > 1 else None
                
                return ResourceEvent(
                    event_type=event_type,
                    resource_name=resource_name,
                    duration=duration,
                    raw_line=line
                )
        
        return None
    
    def _extract_resource_name(self, full_name: str) -> str:
        """Extract resource name from full Terraform resource name."""
        # Example: "aws_instance.web_server" -> "web_server"
        if '.' in full_name:
            return full_name.split('.', 1)[1]
        return full_name
    
    def format_event(self, event: ResourceEvent) -> str:
        """Format a single resource event according to Format A."""
        if event.event_type == ResourceEventType.CREATING:
            return f"🔨 Creating {event.resource_name}..."
        elif event.event_type == ResourceEventType.CREATED:
            duration_text = f" ({event.duration})" if event.duration else ""
            return f"✅ Created {event.resource_name}{duration_text}"
        elif event.event_type == ResourceEventType.MODIFYING:
            return f"🔧 Modifying {event.resource_name}..."
        elif event.event_type == ResourceEventType.MODIFIED:
            duration_text = f" ({event.duration})" if event.duration else ""
            return f"✅ Modified {event.resource_name}{duration_text}"
        elif event.event_type == ResourceEventType.DESTROYING:
            return f"🗑️ Destroying {event.resource_name}..."
        elif event.event_type == ResourceEventType.DESTROYED:
            duration_text = f" ({event.duration})" if event.duration else ""
            return f"✅ Destroyed {event.resource_name}{duration_text}"
        
        return event.raw_line 