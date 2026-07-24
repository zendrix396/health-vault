import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("TEST 1: RAG - Ingest CSV data into vector store")
print("=" * 60)

import pandas as pd
from data_cleaner import convert_csv_to_model_format, update_json_data
import tempfile, json

TMP = tempfile.gettempdir()
JSON_PATH = os.path.join(TMP, "output.json")

if os.path.exists(JSON_PATH):
    os.remove(JSON_PATH)

df = pd.read_csv("data.csv")
cleaned = convert_csv_to_model_format(df)
update_json_data(cleaned, json_file=JSON_PATH)
print(f"Prepared {len(cleaned)} records")

import rag
count = rag.ingest_training_data(JSON_PATH)
print(f"Ingested {count} records into vector store")

print("\n" + "=" * 60)
print("TEST 2: RAG - Query vector store")
print("=" * 60)

docs = rag.query_relevant_docs("fever and cough in young male", n_results=3)
for i, doc in enumerate(docs, 1):
    print(f"\n[{i}] (dist={doc['distance']:.3f})")
    print(f"    Disease: {doc['metadata']['disease']}")
    print(f"    Symptoms: {doc['metadata']['symptoms']}")
    print(f"    Medicine: {doc['metadata']['medicine']}")

context = rag.build_rag_context("What medicine for chest pain and difficulty breathing?", n_results=3)
print(f"\nRAG Context:\n{context}")

print("\n" + "=" * 60)
print("TEST 3: Groq LLM - Generate response")
print("=" * 60)

import groq_llm
response = groq_llm.generate_response(
    "What are common symptoms of diabetes?",
    rag_context=context
)
print(f"Groq response:\n{response}")

print("\n" + "=" * 60)
print("TEST 4: Groq LLM - Medical report analysis")
print("=" * 60)

sample_report = """
Patient: John Doe, Age: 45, Male
Diagnosis: Type 2 Diabetes Mellitus
HbA1c: 8.2% (target <7%)
Fasting glucose: 180 mg/dL
Blood Pressure: 140/90 mmHg
Medications: Metformin 500mg twice daily
Recommendations: Continue current medication, diet modification, exercise plan
"""

analysis = groq_llm.analyze_medical_report(sample_report, language="english")
print(f"Analysis:\n{analysis}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
