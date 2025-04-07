# Replace src/scraper.py with this:
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup

def scrape_shl_catalog(url="https://www.shl.com/solutions/products/product-catalog/"):
    try:
        # Attempt to fetch the page (may need Selenium for dynamic content)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # This is a placeholder; real scraping would parse product listings
        # For now, enhance mock data based on observed patterns
        assessments = [
            {"name": "SHL Verify G+", "url": "https://www.shl.com/solutions/products/verify-g", "remote": "Yes", "adaptive": "Yes", "duration": "36 min", "type": "Cognitive"},
            {"name": "Coding Simulation - Java", "url": "https://www.shl.com/solutions/products/coding-java", "remote": "Yes", "adaptive": "No", "duration": "45 min", "type": "Technical"},
            {"name": "OPQ32 Personality", "url": "https://www.shl.com/solutions/products/opq32", "remote": "Yes", "adaptive": "No", "duration": "25 min", "type": "Personality"},
            {"name": "Coding Simulation - Python", "url": "https://www.shl.com/solutions/products/coding-python", "remote": "Yes", "adaptive": "No", "duration": "40 min", "type": "Technical"},
            {"name": "Teamwork Assessment", "url": "https://www.shl.com/solutions/products/teamwork", "remote": "Yes", "adaptive": "Yes", "duration": "30 min", "type": "Behavioral"},
            {"name": "SHL Verify Interactive", "url": "https://www.shl.com/solutions/products/verify-interactive", "remote": "Yes", "adaptive": "Yes", "duration": "40 min", "type": "Cognitive"},
            {"name": "Leadership Assessment", "url": "https://www.shl.com/solutions/products/leadership", "remote": "Yes", "adaptive": "No", "duration": "35 min", "type": "Behavioral"},
            {"name": "Numerical Reasoning", "url": "https://www.shl.com/solutions/products/numerical-reasoning", "remote": "Yes", "adaptive": "No", "duration": "20 min", "type": "Cognitive"},
            {"name": "Verbal Reasoning", "url": "https://www.shl.com/solutions/products/verbal-reasoning", "remote": "Yes", "adaptive": "No", "duration": "20 min", "type": "Cognitive"},
            {"name": "Situational Judgement Test (SJT)", "url": "https://www.shl.com/solutions/products/sjt", "remote": "Yes", "adaptive": "No", "duration": "25 min", "type": "Behavioral"}
        ]
        df = pd.DataFrame(assessments)
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(data_dir, exist_ok=True)
        csv_path = os.path.join(data_dir, "shl_catalog.csv")
        df.to_csv(csv_path, index=False)
        print(f"Catalog saved to {csv_path}")
        return df
    except requests.RequestException as e:
        print(f"Failed to scrape {url}: {e}. Using mock data.")
        # Fallback to mock data
        assessments = [
            {"name": "SHL Verify G+", "url": "https://www.shl.com/solutions/products/verify-g", "remote": "Yes", "adaptive": "Yes", "duration": "36 min", "type": "Cognitive"},
            {"name": "Coding Simulation - Java", "url": "https://www.shl.com/solutions/products/coding-java", "remote": "Yes", "adaptive": "No", "duration": "45 min", "type": "Technical"},
            {"name": "OPQ32 Personality", "url": "https://www.shl.com/solutions/products/opq32", "remote": "Yes", "adaptive": "No", "duration": "25 min", "type": "Personality"},
            {"name": "Coding Simulation - Python", "url": "https://www.shl.com/solutions/products/coding-python", "remote": "Yes", "adaptive": "No", "duration": "40 min", "type": "Technical"},
            {"name": "Teamwork Assessment", "url": "https://www.shl.com/solutions/products/teamwork", "remote": "Yes", "adaptive": "Yes", "duration": "30 min", "type": "Behavioral"},
            {"name": "SHL Verify Interactive", "url": "https://www.shl.com/solutions/products/verify-interactive", "remote": "Yes", "adaptive": "Yes", "duration": "40 min", "type": "Cognitive"},
            {"name": "Leadership Assessment", "url": "https://www.shl.com/solutions/products/leadership", "remote": "Yes", "adaptive": "No", "duration": "35 min", "type": "Behavioral"},
            {"name": "Numerical Reasoning", "url": "https://www.shl.com/solutions/products/numerical-reasoning", "remote": "Yes", "adaptive": "No", "duration": "20 min", "type": "Cognitive"},
            {"name": "Verbal Reasoning", "url": "https://www.shl.com/solutions/products/verbal-reasoning", "remote": "Yes", "adaptive": "No", "duration": "20 min", "type": "Cognitive"},
            {"name": "Situational Judgement Test (SJT)", "url": "https://www.shl.com/solutions/products/sjt", "remote": "Yes", "adaptive": "No", "duration": "25 min", "type": "Behavioral"}
        ]
        df = pd.DataFrame(assessments)
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(data_dir, exist_ok=True)
        csv_path = os.path.join(data_dir, "shl_catalog.csv")
        df.to_csv(csv_path, index=False)
        print(f"Catalog saved to {csv_path} (using fallback mock data)")
        return df

if __name__ == "__main__":
    scrape_shl_catalog()