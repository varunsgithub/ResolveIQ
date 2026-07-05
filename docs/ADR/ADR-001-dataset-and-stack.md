# Dataset Choice

Selection of CFPB was done because:
    1. Data was available in the public domain. Ready to use and free API.
    2. There is good structure to the data without the need for implementing major data sanitization pipelines.
    3. Realtime data which is updated approximately 15 days from the complaint resolution.

(MIMIC and OList were two possible dataset contenders, both have good structure but were not selected as they required credentialing
and the turn around time for complaint resolution to publishing date was slightly higher.)


# Tech Stack
Database: (Postgres + pgvector) - havent thought about alternatives yet
Orchestration: (Airflow) - ''
Human In The Loop Workflow: Airflow - '' 
Agent Framework: Langchain
Python for ML: 3.11

# Misc Notes:
AWS region: us-east-1