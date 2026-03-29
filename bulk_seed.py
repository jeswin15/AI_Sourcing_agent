import os
import sys
import random
import uuid
from datetime import datetime, timedelta

# Fix import paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

from src.database.factory import get_db

# Thesis data components
SECTORS = ["Blockchain", "Biotech", "HealthTech", "Commerce", "SpaceTech", "AI/ML", "CleanTech"]
STAGES = ["Pre-Seed", "Seed", "Series A", "Series B"]
SOURCES = ["TechCrunch", "EU-Startups", "Sifted", "YCombinator-Blog", "HackerNews", "Reddit"]
LOCATIONS = ["San Francisco, USA", "New York, USA", "London, UK", "Paris, France", "Berlin, Germany", "Stockholm, Sweden", "Toronto, Canada", "Austin, USA"]

PREFIXES = ["Nova", "Bio", "Chain", "Quantum", "Astra", "Eco", "Neo", "Flux", "Core", "Zenith", "Omni", "Synthetix", "Pulse", "Terra", "Vortex"]
SUFFIXES = ["Labs", "Systems", "Health", "Dynamics", "Solutions", "Networks", "Flow", "Logic", "Intelligence", "Ventures", "Space", "Growth", "Bio", "Grid", "Link"]

SDGS = [
    "SDG 3: Good Health and Well-being",
    "SDG 7: Affordable and Clean Energy",
    "SDG 9: Industry, Innovation and Infrastructure",
    "SDG 12: Responsible Consumption and Production",
    "SDG 13: Climate Action",
    "SDG 14: Life Below Water"
]

DESC_TEMPLATES = [
    "Developing a {0} platform for {1} with integrated {2}.",
    "Pioneering {0} technologies targeting the {1} market in {2}.",
    "Building {0} specifically for {1} to improve {2}.",
    "The world's first {0} specifically designed for {1} in {2}.",
    "Leveraging {0} for {1} and {2} efficiency."
]

DESC_KEYWORDS = [
    ["decentralized", "secure", "immutable", "consensus-driven"],
    ["precision", "molecular", "gene-editing", "next-gen"],
    ["automated", "scalable", "high-performance", "sustainable"],
    ["connected", "low-latency", "edge-computing", "smart"]
]

RATIONALE_TEMPLATES = [
    "Strong fit for {0} focus. Highly innovative team based in {1}. Direct SDG alignment.",
    "Strategic alignment with {0} thesis. Significant potential in {1}. High innovation score.",
    "Great candidate for {0} pipeline. Fits stage ({1}) and sector requirements perfectly.",
    "Promising {0} startup. Improving {1} via novel {2} architecture."
]

def generate_startup(i):
    sector = random.choice(SECTORS)
    stage = random.choice(STAGES)
    source = random.choice(SOURCES)
    location = random.choice(LOCATIONS)
    
    name = random.choice(PREFIXES) + random.choice(SUFFIXES)
    if random.random() > 0.8: name += f" {random.randint(1, 99)}"
    
    desc = random.choice(DESC_TEMPLATES).format(
        random.choice(random.choice(DESC_KEYWORDS)),
        sector.lower(),
        "performance" if random.random() > 0.5 else "sustainability"
    )
    
    # Random score breakdown
    sector_score = random.randint(12, 20)
    geo_score = random.randint(12, 20)
    funding_score = random.randint(10, 20)
    sdg_score = random.randint(10, 20)
    innovation_score = random.randint(10, 20)
    
    total = sector_score + geo_score + funding_score + sdg_score + innovation_score
    
    # Random timestamp within last 30 days
    days_ago = random.randint(0, 30)
    hours_ago = random.randint(0, 23)
    ts = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).isoformat()
    
    return {
        "company_name": name,
        "description": desc,
        "industry": sector,
        "stage": stage,
        "funding_info": f"Raising ${random.randint(1, 10)}M" if random.random() > 0.3 else f"${random.randint(500, 900)}k Seed",
        "sdg_alignment": random.choice(SDGS),
        "innovation_level": "High" if total > 75 else "Medium" if total > 55 else "Low",
        "confidence_score": total,
        "score_breakdown": {
            "sector": sector_score,
            "geography": geo_score,
            "funding": funding_score,
            "sdg": sdg_score,
            "innovation": innovation_score
        },
        "rationale": random.choice(RATIONALE_TEMPLATES).format(sector, location, name),
        "recommendation": "Progress" if total > 80 else "Save" if total > 60 else "Ignore",
        "source": source,
        "link": f"https://mocklink.io/{uuid.uuid4().hex[:12]}",
        "status": random.choice(["Pending", "Pending", "Pending", "Save", "Ignore"]),
        "timestamp": ts,
        "location": location
    }

def bulk_seed(count=250):
    db = get_db()
    print(f"Starting bulk seed of {count} startups...")
    
    startups = [generate_startup(i) for i in range(count)]
    
    inserted = 0
    for s in startups:
        if db.insert_startup(s):
            inserted += 1
            if inserted % 25 == 0:
                print(f"  Processed {inserted}/{count}...")
    
    print(f"\nDone! Successfully seeded {inserted} new startups.")
    print(f"Total startups in DB: {len(db.get_all_startups())}")

if __name__ == "__main__":
    count = 250
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    bulk_seed(count)
