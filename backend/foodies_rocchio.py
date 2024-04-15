# -*- coding: utf-8 -*-
"""FOODIE$_generatecossim.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ECal3YrKCy240iBwKr4VvzFKCdHXQcyM
"""

import pandas as pd
import numpy as np
from numpy import linalg as LA
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# loading dataset
#df = pd.read_csv("dataset.csv")

def rocchio_results(df, query, price_range):
  #print("Value of price_range:", price_range)
  final_price = price_range
  if price_range == '2': 
    final_price = "$"
  elif price_range == '3': 
    final_price = "$$"
  elif price_range == '4': 
    final_price = "$$$"

  #Uses the Comments column and creates the TF-IDF matrix
  reviews = df['comments'].tolist()
  tfidf_vectorizer = TfidfVectorizer()
  tfidf_matrix = tfidf_vectorizer.fit_transform(reviews).toarray() # 3060 x 6506 matrix
  tfidf_matrix # currently very sparse - an option is to make it dense but more costly in memory

  """This is an example query which should be switched out to the user input"""

  query_tfidf = tfidf_vectorizer.transform([query]).toarray()

  types = set()

  for entry in df["type"]:
    temp = re.findall(r'[a-z]+', entry.lower())
    for val in temp:
      types.add(val)

  """Tokenizes the query and makes a set of the restaurant types in the query"""

  qtokens = re.findall(r'[a-z]+', query.lower())
  qtokens = set(qtokens)
  qtypes = set()
  for t in qtokens:
    if t in types:
      qtypes.add(t)

  relevant_docs = []  # list of relevant document indices
  non_relevant_docs = []  # list of non-relevant document indices

  # Rocchio algorithm parameters
  alpha = 1  # weight for the query vector
  beta = 0.75  # weight for the relevant documents vector
  gamma = 0.25  # weight for the non-relevant documents vector

  # Updating the query vector based on relevant and non-relevant documents
  query_vector = alpha * query_tfidf  # initialize query vector with alpha * query_tfidf

  if relevant_docs:
    relevant_vectors = tfidf_matrix[relevant_docs]
    relevant_vector = np.mean(relevant_vectors, axis=0)  # calculate the mean vector of relevant documents
    query_vector += beta * relevant_vector  # update query vector with beta * relevant_vector

  if non_relevant_docs:
    non_relevant_vectors = tfidf_matrix[non_relevant_docs]
    non_relevant_vector = np.mean(non_relevant_vectors, axis=0)  # calculate the mean vector of non-relevant documents
    query_vector -= gamma * non_relevant_vector  # update query vector with gamma * non_relevant_vector

  # Calculate cosine similarity between updated query vector and all documents
  rocchio_cossims = []
  for i in range(len(tfidf_matrix)):
    doc = tfidf_matrix[i]
    mov1norm = np.sqrt(np.sum(np.square(query_vector)))  # get the norm of the vector
    mov2norm = np.sqrt(np.sum(np.square(doc)))  # get the norm of the vector
    num = np.dot(query_vector, doc)  # dot product the vectors
    den = mov1norm * mov2norm  # dot product the norms
    if den == 0:
      rocchio_cossims.append((i, 0))
    else:
      temp = num / den
      rocchio_cossims.append((i, temp))

  rocchio_cossims_sorted = sorted(rocchio_cossims, key=lambda x: x[1], reverse=True)

  # Print the top 5 results after applying Rocchio algorithm
  #print("Rocchio Results:")
  final = []
  threshold = 5
  if len(qtypes) == 0 or len(rocchio_cossims_sorted) < threshold:
    for i in range(100):
      #if df.loc[i, 'price_range'] == final_price:
        final.append(df.at[rocchio_cossims_sorted[i][0], 'name'])
  else:
    for i in range(100):
      #if df.loc[i, 'price_range'] == final_price:
        final.append(df.at[rocchio_cossims_sorted[i][0], 'name'])
  return final 
  