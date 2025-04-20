from typing import List, Literal, Optional, TypedDict

# Field related types
FieldType = Literal[
    "date", "text", "number", "currency", "select", "multiSelect",
    "multiCollaborator", "createdBy", "lastUpdatedBy", "createdAt", "updatedAt"
]

class SelectOption(TypedDict):
    """Option for select and multiSelect fields"""
    id: str
    name: str

class FieldConfig(TypedDict, total=False):
    """Field configuration based on type"""
    fractionDigits: Optional[int]  # for number and currency
    currency: str  # for currency
    options: List[SelectOption]  # for select and multiSelect
    includeTime: bool  # for createdAt and lastUpdatedAt

class FieldProps(TypedDict):
    """Field properties as per API specification"""
    object: str
    id: str
    type: FieldType
    name: str
    config: Optional[FieldConfig] 