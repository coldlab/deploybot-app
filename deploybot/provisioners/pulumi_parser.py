import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class PulumiEventType(Enum):
    """Types of Pulumi events."""
    RESOURCE_CREATE = "create"
    RESOURCE_UPDATE = "update"
    RESOURCE_DELETE = "delete"
    RESOURCE_REPLACE = "replace"
    RESOURCE_READ = "read"
    STACK_UPDATE = "stack_update"
    DIAGNOSTIC = "diagnostic"
    OUTPUT = "output"
    UNKNOWN = "unknown"

@dataclass
class PulumiEvent:
    """Represents a parsed Pulumi event."""
    event_type: PulumiEventType
    resource_type: Optional[str] = None
    resource_name: Optional[str] = None
    operation: Optional[str] = None
    status: Optional[str] = None
    duration: Optional[str] = None
    message: Optional[str] = None
    raw_line: str = ""

class PulumiOutputParser:
    """Parser for Pulumi command output."""
    
    def __init__(self):
        # Resource operation patterns
        self.resource_patterns = [
            # + pulumi:providers:gcp default_8_36_0 creating (0s)
            r'^\s*([+\-~])\s+([^:]+):([^:]+):([^\s]+)\s+([^\s]+)\s+\(([^)]+)\)',
            # + pulumi:pulumi:Stack simple-web-server-gcp-dev creating (0s)
            r'^\s*([+\-~])\s+([^:]+):([^:]+):([^\s]+)\s+([^\s]+)',
            # @ updating..........
            r'^\s*@\s+([^\s]+)',
        ]
        
        # Diagnostic patterns
        self.diagnostic_patterns = [
            # error: pulumi:providers:gcp resource 'default_8_36_0' has a problem
            r'^\s*(error|warning|info):\s+([^:]+):([^:]+):([^:]+)\s+(.+)',
            # error: Program failed with an unhandled exception
            r'^\s*(error|warning|info):\s+(.+)',
        ]
        
        # Output patterns
        self.output_patterns = [
            # Project ID: coldlab-central
            r'^\s*([^:]+):\s+(.+)',
        ]
        
        # Stack update patterns
        self.stack_patterns = [
            # Updating (dev):
            r'^\s*(Updating|Creating|Destroying)\s+\(([^)]+)\):',
            # Resources: + 1 created
            r'^\s*Resources:\s+(.+)',
            # Duration: 23s
            r'^\s*Duration:\s+(.+)',
        ]
    
    def parse_line(self, line: str) -> Optional[PulumiEvent]:
        """Parse a single line of Pulumi output."""
        line = line.strip()
        if not line:
            return None
        
        # Try resource patterns first
        for pattern in self.resource_patterns:
            match = re.match(pattern, line)
            if match:
                return self._parse_resource_event(match, line)
        
        # Try diagnostic patterns
        for pattern in self.diagnostic_patterns:
            match = re.match(pattern, line)
            if match:
                return self._parse_diagnostic_event(match, line)
        
        # Try output patterns
        for pattern in self.output_patterns:
            match = re.match(pattern, line)
            if match:
                return self._parse_output_event(match, line)
        
        # Try stack patterns
        for pattern in self.stack_patterns:
            match = re.match(pattern, line)
            if match:
                return self._parse_stack_event(match, line)
        
        # Unknown event
        return PulumiEvent(
            event_type=PulumiEventType.UNKNOWN,
            message=line,
            raw_line=line
        )
    
    def _parse_resource_event(self, match: re.Match, line: str) -> PulumiEvent:
        """Parse a resource operation event."""
        groups = match.groups()
        
        if len(groups) >= 6:
            # Full resource pattern
            operation, provider, resource_type, resource_name, status, duration = groups[:6]
        elif len(groups) >= 5:
            # Stack pattern
            operation, provider, resource_type, resource_name, status = groups[:5]
            duration = None
        else:
            # Update pattern
            operation = groups[0]
            provider = resource_type = resource_name = status = duration = None
        
        # Determine event type from operation
        if operation == '+':
            event_type = PulumiEventType.RESOURCE_CREATE
        elif operation == '-':
            event_type = PulumiEventType.RESOURCE_DELETE
        elif operation == '~':
            event_type = PulumiEventType.RESOURCE_UPDATE
        elif operation == '@':
            event_type = PulumiEventType.STACK_UPDATE
        else:
            event_type = PulumiEventType.UNKNOWN
        
        return PulumiEvent(
            event_type=event_type,
            resource_type=resource_type,
            resource_name=resource_name,
            operation=operation,
            status=status,
            duration=duration,
            raw_line=line
        )
    
    def _parse_diagnostic_event(self, match: re.Match, line: str) -> PulumiEvent:
        """Parse a diagnostic event (error, warning, info)."""
        groups = match.groups()
        
        if len(groups) >= 5:
            # Full diagnostic pattern
            level, provider, resource_type, resource_name, message = groups[:5]
        else:
            # Simple diagnostic pattern
            level, message = groups[:2]
            provider = resource_type = resource_name = None
        
        return PulumiEvent(
            event_type=PulumiEventType.DIAGNOSTIC,
            resource_type=resource_type,
            resource_name=resource_name,
            status=level,
            message=message,
            raw_line=line
        )
    
    def _parse_output_event(self, match: re.Match, line: str) -> PulumiEvent:
        """Parse an output event."""
        key, value = match.groups()
        
        return PulumiEvent(
            event_type=PulumiEventType.OUTPUT,
            resource_name=key,
            message=value,
            raw_line=line
        )
    
    def _parse_stack_event(self, match: re.Match, line: str) -> PulumiEvent:
        """Parse a stack-level event."""
        groups = match.groups()
        
        if len(groups) >= 2:
            operation, stack_name = groups[:2]
        else:
            operation = groups[0]
            stack_name = None
        
        return PulumiEvent(
            event_type=PulumiEventType.STACK_UPDATE,
            resource_name=stack_name,
            operation=operation,
            message=line,
            raw_line=line
        )
    
    def format_event(self, event: PulumiEvent) -> str:
        """Format a Pulumi event for display."""
        if event.event_type == PulumiEventType.RESOURCE_CREATE:
            return f"🟢 Creating {event.resource_type}:{event.resource_name}"
        elif event.event_type == PulumiEventType.RESOURCE_UPDATE:
            return f"🟡 Updating {event.resource_type}:{event.resource_name}"
        elif event.event_type == PulumiEventType.RESOURCE_DELETE:
            return f"🔴 Deleting {event.resource_type}:{event.resource_name}"
        elif event.event_type == PulumiEventType.RESOURCE_REPLACE:
            return f"🔄 Replacing {event.resource_type}:{event.resource_name}"
        elif event.event_type == PulumiEventType.DIAGNOSTIC:
            if event.status == "error":
                return f"❌ Error: {event.message}"
            elif event.status == "warning":
                return f"⚠️ Warning: {event.message}"
            else:
                return f"ℹ️ Info: {event.message}"
        elif event.event_type == PulumiEventType.OUTPUT:
            return f"📋 {event.resource_name}: {event.message}"
        elif event.event_type == PulumiEventType.STACK_UPDATE:
            return f"🔄 {event.operation} {event.resource_name or 'stack'}"
        else:
            return event.raw_line
    
    def parse_output(self, output: str) -> List[PulumiEvent]:
        """Parse entire Pulumi output and return list of events."""
        events = []
        for line in output.split('\n'):
            event = self.parse_line(line)
            if event:
                events.append(event)
        return events 