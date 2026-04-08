import faiss
import numpy as np

dimension = 384
index = faiss.IndexFlatL2(dimension)
doc_mapping = []

users = []
roles = []
documents = []
