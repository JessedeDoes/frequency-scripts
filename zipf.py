import requests
import csv
import matplotlib.pyplot as plt
import os
import re
import json
import sys
import scipy


def postprocess(freqs,f):
    nfreqs = {}
    for k in freqs.keys():
        x = freqs[k]
        mapped = f(k)
        if mapped is not None:
            if mapped in nfreqs:
              nfreqs[mapped] += x
            else:
              nfreqs[mapped] = x
    return nfreqs

def relative(freqs):
    relfreqs = {}
    total = sum(freqs.values())
    for k in freqs.keys():
        relfreqs[k] = freqs[k] / total
    return relfreqs
    
    
pos_mapping = {
"n" : "Zelfstandig naamwoord",
"ww" : "Werkwoord",
"let" : "Interpunctie",
"vz" : "Voorzetsel",
"spec" : "Overig",
"vnw" : "Voornaamwoord en lidwoord",
"lid" : "Voornaamwoord en lidwoord",
"adj" : "Bijvoeglijk naamwoord",
"bw" : "Bijwoord",
"vg" : "Voegwoord",
"tw" : "Telwoord",
"tsw" : "Tussenwerpsel"
}

def pos_mapped(p):
    pos_head = re.sub("[^A-Za-z].*", "", p)
    print(f"{p} {pos_head}")
    if pos_head in pos_mapping:
        m = pos_mapping[pos_head]
        if re.match("n.*eigen.*|spec.*deelei.*", p):
            return "Eigennaam"
        return pos_mapping[pos_head]
    else:
       return None


# BlackLab Server configuration
BASE_URL = "http://svprmc33.ivdnt.loc/blacklab-server-new/opensonar/hits-csv/"
BASE_URL="http://svotmc10.ivdnt.loc/blacklab-server/GCND/hits-csv/"
#http://svatai01.ivdnt.loc/blacklab-server/chn-refcorpus/termfreq?annotation=word_ng2&number=10
BASE_URL="http://svotmc10.ivdnt.loc/blacklab-server/GCND/termfreq/"
BASE_URL="http://svprmc33.ivdnt.loc/blacklab-server-new/opensonar/termfreq"

INDEX_NAME = "your-index-name"
ANNOTATION = "pos"
CHUNK_SIZE = 1000
OUTPUT_CSV = "frequency_list.csv"
MAX=1000


def download_frequency_list(base_url, index_name, ANNOTATION, chunk_size, output_csv, pos_mapping=None,max=MAX):
    """Downloads frequency list chunked by the specified size and saves as CSV."""
    start = 0
    headers_written = False

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = None
       
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
      
        csvfile.write("word,frequency\n")
        allKeys = {}
        while True:
         
  
            params = {
                "outputformat": "json",
                "patt": "[]",
                "annotation": f"{ANNOTATION}",
      
                "first": start,
                "number": chunk_size,
                #"listvalues": "word,lemma,pos,phonetic",

                #"indexname": index_name
            }
           

            print(f"Fetching: {base_url} with params {params}")
            response = requests.get(base_url, params=params)


            if response.status_code != 200:
                print(f"Error fetching data: {response.status_code} {response.text}")
                break


            freqs = json.loads(response.text)['termFreq']
           
            if pos_mapping is not None:
                freqs = postprocess(freqs,pos_mapping)
                freqs = relative(freqs)
                #print(freqs)

            # print(response.text)

            newInfo = any((not key in allKeys) for key in freqs)

            if newInfo and (max is None or not start > max): 
                for x in list(freqs.keys()):
                    print(x)
                    #csvfile.write(f"{x},{freqs[x]}\n")
                    
                    allKeys[x]  = freqs[x]
                    csvwriter.writerows([[x,freqs[x]]])
                    csvfile.flush()
            else:
                return
            start += chunk_size

    print(f"Frequency list saved to {output_csv}")

def plot_frequencies(csv_file):
    """Plots word frequencies from a CSV file."""
    words = []
    frequencies = []

    with open(csv_file, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            words.append(row["word"])
            frequencies.append(int(row["frequency"]))

    plt.figure(figsize=(10, 6))
    plt.bar(words[:50], frequencies[:50], color="blue")  # Plot top 50 words
    plt.xlabel("Words")
    plt.ylabel("Frequencies")
    plt.title("Word Frequencies")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    pdf_file = re.sub(".csv", ".pdf", csv_file)
    plt.savefig(pdf_file, format="pdf", bbox_inches="tight")
    #plt.show()

def plot_frequencies_with_zipf(csv_file,n, words_only=False):
    """Plots word frequencies from a CSV file and fits a Zipf curve."""
    import numpy as np
    from scipy.optimize import curve_fit
    import matplotlib.pyplot as plt

    def zipf_law(rank, k):
        """Zipf's law formula: frequency = k / rank."""
        return k / rank

    words = []
    frequencies = []
    freqs = {}
    with open(csv_file, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            w=row["word"]
            if (not words_only) or re.fullmatch(r"\w+", w):
                words.append(row["word"])
                freqs[w] = float(row["frequency"])
                frequencies.append(float(row["frequency"]))

    # Sort frequencies in descending order
    sorted_frequencies = sorted(frequencies, reverse=True)[:n] # maar woorden niet....
    sorted_words = sorted(words, key=freqs.get, reverse=True)
    ranks = np.arange(1, len(sorted_frequencies) + 1)

    # Fit Zipf's law curve
    popt, _ = curve_fit(zipf_law, ranks, sorted_frequencies)
    fitted_frequencies = zipf_law(ranks, *popt)

    plt.figure(figsize=(10, 6))
    plt.bar(sorted_words[:n], sorted_frequencies, color="blue", label="Frequenties in corpus")  # Plot top n words
    k = popt[0] 
    plt.plot(sorted_words[:n], fitted_frequencies, color="red", linestyle="--", label=f"Zipf-curve, k={k:.2f}")

    plt.xlabel("Woorden")
    plt.ylabel("Frequenties")
    plt.title("Woordfrequenties (OpenSoNaR+) met best passende Zipf-curve")
    plt.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    pdf_file = re.sub(".csv", ".pdf", csv_file)
    plt.savefig(pdf_file, format="pdf", bbox_inches="tight")
    #plt.show()

if __name__ == "__main__":
    if os.path.exists(OUTPUT_CSV):
        os.remove(OUTPUT_CSV)  # Remove existing CSV to start fresh
    OUTPUT_CSV="Data/pos-frequencies.csv"
    
    download_frequency_list(BASE_URL, INDEX_NAME, "pos", CHUNK_SIZE, OUTPUT_CSV,pos_mapping=pos_mapped)
    plot_frequencies_with_zipf(OUTPUT_CSV,1000)


    OUTPUT_CSV="Data/word-frequencies.csv"
    download_frequency_list(BASE_URL, INDEX_NAME, "word", CHUNK_SIZE, OUTPUT_CSV,pos_mapping=None)
    plot_frequencies_with_zipf(OUTPUT_CSV,50,words_only=True)
   
