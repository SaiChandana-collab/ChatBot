from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd

df = pd.read_csv("Home Remedies (1).csv")

health_issues = df['Health Issue'].astype(str).tolist()

embedder = SentenceTransformer('all-mpnet-base-v2')


embeddings = embedder.encode(health_issues, convert_to_numpy=True)
np.save("C:/Users/user/OneDrive/Documents/health_issues_embeddings.npy", embeddings)