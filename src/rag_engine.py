# Replace src/rag_engine.py with this:
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import pandas as pd
from dotenv import load_dotenv
import os
import google.generativeai as genai
import logging
import re
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY not found in .env file")
    raise ValueError("GEMINI_API_KEY not found in .env file")
logger.info(f"Loaded API Key: {api_key[:4]}... (partial for security)")
genai.configure(api_key=api_key)

class RAGEngine:
    def __init__(self, catalog_path=os.path.join(os.path.dirname(__file__), "..", "data", "shl_catalog.csv")):
        self.df = pd.read_csv(catalog_path)
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = self._build_vector_store()
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def _build_vector_store(self):
        texts = self.df.apply(lambda row: f"{row['name']} {row['type']} {row['duration']}", axis=1).tolist()
        return FAISS.from_texts(texts, self.embeddings)

    def recommend(self, query, max_results=10):
        # Vector search for initial filtering
        docs = self.vector_store.similarity_search(query, k=15)
        initial_results = [self.df.iloc[int(doc.metadata.get("index", i))] for i, doc in enumerate(docs)]
        
        # Extract max duration if specified in query
        max_duration = None
        duration_match = re.search(r'max\s+(\d+)\s*(min|minutes)|under\s+(\d+)\s*(min|minutes)', query.lower())
        if duration_match:
            max_duration = int(duration_match.group(1) or duration_match.group(3))
            initial_results = [row for row in initial_results if not max_duration or int(row['duration'].split()[0]) <= max_duration]

        # Convert initial_results list to a string for the prompt
        assessments_str = "\n".join([f"{row['name']} (URL: {row['url']}, Duration: {row['duration']}, Type: {row['type']}, Remote: {row['remote']}, Adaptive: {row['adaptive']})" for row in initial_results])
        logger.info(f"Available assessments: {assessments_str or 'No assessments meet the time constraint.'}")

        # Enhanced prompt for Gemini
        prompt = f"""
        Given the query '{query}', recommend up to {max_results} SHL assessments from the following list that best match the job role and constraints. 
        Strictly adhere to the time limit if specified (e.g., max 40 min or under 25 minutes), and do not recommend assessments that exceed it. 
        Provide a numbered list with the assessment name, URL, and a brief reasoning, including a confidence score between 0 and 1. 
        Format your response as:
        1. Assessment Name (URL: [URL]) - Reasoning (confidence: 0.x)
        2. Assessment Name (URL: [URL]) - Reasoning (confidence: 0.x)
        ...

        Available assessments:
        {assessments_str or 'No assessments meet the time constraint.'}
        """
        
        max_retries = 3
        retry_delay = 60  # seconds
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1} to generate content for query: {query}")
                response = self.model.generate_content(prompt)
                response_text = response.text.strip()
                logger.info(f"Gemini Response: {response_text}")
                break
            except google.api_core.exceptions.ResourceExhausted as e:
                logger.warning(f"Quota exceeded on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                else:
                    raise
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                raise

        # Parse the response to extract recommendations
        recommendations = []
        lines = response_text.split('\n')
        in_recommendations = False
        for line in lines:
            line = line.strip()
            if line.startswith(tuple(str(i) for i in range(1, max_results + 1))) and '- ' in line and '(confidence:' in line:
                in_recommendations = True
                match = re.match(r'(\d+)\.\s+(.+?)\s+\(URL:\s*([^\)]+)\)\s+-\s+(.+?)\s+\(confidence:\s*(\d+\.\d+)\)', line)
                if match:
                    name = match.group(2).strip()
                    url = match.group(3).strip()
                    reasoning = match.group(4).strip()
                    confidence = float(match.group(5))
                    matching_row = self.df[(self.df['name'].str.contains(name, case=False, na=False)) & (self.df['url'].str.contains(url, case=False, na=False))]
                    if not matching_row.empty:
                        row = matching_row.iloc[0]
                        logger.info(f"Matched: {name} -> {row['name']} (Duration: {row['duration']})")
                        recommendations.append({
                            "name": row["name"],
                            "url": row["url"],
                            "remote": row["remote"],
                            "adaptive": row["adaptive"],
                            "duration": row["duration"],
                            "type": row["type"],
                            "reasoning": reasoning,
                            "confidence": confidence
                        })
                else:
                    logger.warning(f"No match for line: {line}")
            elif not in_recommendations and line:
                logger.info(f"Skipping non-recommendation line: {line}")

        # Sort by confidence and limit to max_results
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        logger.info(f"Final recommendations: {len(recommendations)} items")
        return recommendations[:max_results]

    def evaluate_recall_map(self, benchmark_path="data/benchmark.csv"):
        df_benchmark = pd.read_csv(benchmark_path)
        recall_at_3 = []
        map_at_3 = []
        for idx, row in df_benchmark.iterrows():
            query = row["queries"]
            ground_truth = eval(row["ground_truth"])  # Assuming list stored as string
            recommendations = self.recommend(query, max_results=3)
            rec_names = [rec["name"] for rec in recommendations]
            # Recall@3
            relevant = len(set(rec_names) & set(ground_truth))
            total_relevant = len(ground_truth)
            recall = relevant / total_relevant if total_relevant > 0 else 0
            recall_at_3.append(recall)
            # MAP@3
            precision_at_k = []
            for k in range(1, 4):
                relevant_k = len(set(rec_names[:k]) & set(ground_truth))
                precision_k = relevant_k / k if k > 0 else 0
                precision_at_k.append(precision_k)
            ap_at_3 = sum(p * (1 if r in ground_truth else 0) for p, r in zip(precision_at_k, rec_names[:3])) / min(3, len(ground_truth))
            map_at_3.append(ap_at_3)
        mean_recall_at_3 = sum(recall_at_3) / len(recall_at_3) if recall_at_3 else 0
        mean_ap_at_3 = sum(map_at_3) / len(map_at_3) if map_at_3 else 0
        logger.info(f"Mean Recall@3: {mean_recall_at_3:.3f}")
        logger.info(f"MAP@3: {mean_ap_at_3:.3f}")
        return mean_recall_at_3, mean_ap_at_3

if __name__ == "__main__":
    engine = RAGEngine()
    engine.evaluate_recall_map()  # Run evaluation
    results = engine.recommend("Looking for software engineers with both technical coding skills and teamwork, max 45 minutes")
    print(results)