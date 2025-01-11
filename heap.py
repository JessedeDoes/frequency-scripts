import requests
import random
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
from scipy.optimize import curve_fit
  
# Function to retrieve random sentences from BlackLab
def get_random_sentences(blacklab_url, total_sentences=100000, random_seed=42,sample_percentage=None):
    """Retrieve random sentences from BlackLab."""
    print(f"Retrieving sentences: {sample_percentage} {total_sentences}")
    random.seed(random_seed)
    sentences = []
    first = 0
    total_tokens = 0
    chunk_size = 5000  # Fetch sentences in chunks
    while len(sentences) < total_sentences:
        number = min(total_sentences - len(sentences), chunk_size)
        
        params = {
            "outputformat": "json",
            "patt": "<s/>",
            "first": first,
            "number": number,
        }
        if sample_percentage is not None:
            params["sample"] = sample_percentage

        try:
          response = requests.get(blacklab_url, params=params)
          response.raise_for_status()
          data = response.json()
          hits = data.get("hits", [])
          l = 0 if not hits else len(hits)
          print(f"...... {len(sentences)} {l} ..... ")
          if not hits or len(hits) == 0:
             print(f"No more hits... {len(sentences)}")
             break  # Stop if there are no more sentences
          for hit in hits:
            s = hit["match"]["word"]
            total_tokens += len(s)
            sentences.append(s)
          first += number
        except:
          break
    
    random.shuffle(sentences)
    
    return sentences,len(sentences), total_tokens # random.shuffle(sentences)

    #return random.sample(sentences, total_sentences)

# Function to calculate TTR
def calculate_token_type_curve(sentences):
    """Calculate the Token-Type curve."""
    tokens = []
    type_count_values = []
    type_counts = Counter()

    for sentence in sentences:

        # Tokenize the sentence (simple whitespace-based for this example)
        words = sentence #.split()
        for w in words:
          #tokens.extend(words)
      
          type_counts.update([w])
        
        
          type_count = len(type_counts) # / len(tokens)
          type_count_values.append(type_count)

    return type_count_values, len(type_counts), len(tokens)

def heap_law(n,k,beta):
    return k* n**beta

# Main function to verify Heaps' law
def verify_heaps_law(blacklab_url, total_sentences=10000,sample_percentage=None,outputFile="Data/heaps_law_verification.pdf"):
    """Retrieve sentences and verify Heaps' law."""
    sentences,n_sentences, total_tokens = get_random_sentences(blacklab_url, total_sentences,sample_percentage=sample_percentage)
  
    ttr_curve, total_types, x = calculate_token_type_curve(sentences)
    ranks = np.arange(1, len(ttr_curve) + 1)
   # Fit Heap's law curve
    popt, _ = curve_fit(heap_law, ranks, ttr_curve)
    k=popt[0]
    beta=popt[1]

    #print(popt)
    fitted_values = heap_law(ranks, *popt)
    #print(list(zip(ttr_curve,fitted_values)))
    # Plotting 
    plt.figure(figsize=(10, 6))

    plt.plot(range(1, len(ttr_curve) + 1), ttr_curve, label="Type Count Curve")
    plt.plot(range(1, len(ttr_curve) + 1), fitted_values, color="red", linestyle="--", label=f"Fitted Heap Curve (k={k:.2f}, β={beta:.2f})")
    
    
    plt.xlabel("Omvang sample")
    plt.ylabel("Aantal types in sample")
    plt.title(f"Heaps' law voor een sample van {total_tokens} tokens uit OpenSoNaR+")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(outputFile, format="pdf", bbox_inches="tight")
    plt.show()

n_sentences=424036# 424036 # 424036 voor een procent
n_sentences_opensonar=42403677
sample_percentage=10

# Example usage
if __name__ == "__main__":
    blacklab_url = "http://svprmc33.ivdnt.loc/blacklab-server-new/opensonar/hits"

    verify_heaps_law(blacklab_url,total_sentences=n_sentences_opensonar,sample_percentage=sample_percentage)

