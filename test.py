import os
from dotenv import load_dotenv

load_dotenv()

neo4j_uri = os.getenv("NEO4J_URI")  # Ensure this matches your .env file
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

print("NEO4J URI:", neo4j_uri)
print(neo4j_user)  # Debugging step

if not neo4j_uri:
    raise ValueError("NEO4J_URI is not set or is empty.")
