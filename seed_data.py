import os
import sys
from datetime import datetime

# Fix import paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

from src.database.factory import get_db

def seed():
    db = get_db()
    
    startups = [
        {
            "company_name": "Nebula Space Labs",
            "description": "Building sustainable satellite propulsion systems using water-based plasma technology. Based in Colorado, USA. Focus on debris mitigation.",
            "industry": "SpaceTech",
            "stage": "Seed",
            "funding_info": "Raising $2M at $10M valuation",
            "sdg_alignment": "SDG 9: Industry, Innovation and Infrastructure",
            "innovation_level": "High",
            "confidence_score": 85,
            "score_breakdown": {"sector": 20, "geography": 18, "funding": 16, "sdg": 15, "innovation": 16},
            "rationale": "Perfect hit for Holocene's Space focus and SDG alignment. Colorado is a prime geography. Strong innovation in sustainable propulsion.",
            "recommendation": "Progress",
            "source": "TechCrunch",
            "link": "https://techcrunch.com/mock/nebula-space",
            "status": "Pending",
            "timestamp": datetime.now().isoformat()
        },
        {
            "company_name": "BioFlow Health",
            "description": "Miniaturized dialysis machines for home-use in sub-Saharan Africa. Headquartered in London. Improving patient accessibility to life-saving care.",
            "industry": "HealthTech",
            "stage": "Series A",
            "funding_info": "$5M raised",
            "sdg_alignment": "SDG 3: Good Health and Well-being",
            "innovation_level": "High",
            "confidence_score": 78,
            "score_breakdown": {"sector": 18, "geography": 20, "funding": 12, "sdg": 18, "innovation": 10},
            "rationale": "Addresses significant gap in healthcare access. London-based (UK/Europe) fits thesis. Direct impact on human wellbeing.",
            "recommendation": "Save",
            "source": "Sifted",
            "link": "https://sifted.eu/mock/bioflow",
            "status": "Pending",
            "timestamp": datetime.now().isoformat()
        },
        {
            "company_name": "ChainGuard Europe",
            "description": "Decentralized supply chain tracking for sustainable fashion brands. Paris-based. Using Ethereum Layer 2 to ensure transparency and ethical sourcing.",
            "industry": "Blockchain",
            "stage": "Pre-Seed",
            "funding_info": "Raising $500k",
            "sdg_alignment": "SDG 12: Responsible Consumption and Production",
            "innovation_level": "Medium",
            "confidence_score": 72,
            "score_breakdown": {"sector": 16, "geography": 20, "funding": 10, "sdg": 14, "innovation": 12},
            "rationale": "Strong fit for Blockchain and SDG-12. Paris location is ideal. Lower funding amount is safe for pre-seed focus.",
            "recommendation": "Save",
            "source": "EU-Startups",
            "link": "https://eu-startups.com/mock/chainguard",
            "status": "Pending",
            "timestamp": datetime.now().isoformat()
        }
    ]

    print(f"Seeding {len(startups)} startups into {os.getenv('DATABASE_TYPE', 'unknown')}...")
    
    # Check if they exist first or just insert
    existing = [s.get("link") for s in db.get_all_startups()]
    
    count = 0
    for s in startups:
        if s["link"] not in existing:
            db.insert_startup(s)
            count += 1
            print(f"  + Added: {s['company_name']}")
    
    print(f"Done. Successfully seeded {count} new startups.")

if __name__ == "__main__":
    seed()
