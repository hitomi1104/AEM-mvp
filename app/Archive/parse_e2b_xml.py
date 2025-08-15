import xml.etree.ElementTree as ET

def parse_e2b_xml(content: bytes):
    root = ET.fromstring(content)
    
    # This is just a mock structure for demo purposes
    return [{
        "reportId": "AEV-00001",
        "eventDate": "2025-07-10",
        "description": "Patient developed severe rash and shortness of breath after 3 days on DrugA.",
        "product": "DrugA",
        "dose": 500,
        "route": "Oral",
        "outcome": ["Hospitalization", "Life-threatening"],
        "source": "Health Professional"
    }]