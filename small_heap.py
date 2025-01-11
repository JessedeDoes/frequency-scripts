import heap
if __name__ == "__main__":
    blacklab_url = "http://svprmc33.ivdnt.loc/blacklab-server-new/opensonar/hits"
    blacklab_url = "http://svotmc10.ivdnt.loc/blacklab-server/GCND/hits"
    #heap.calculate_token_type_curve([['hallo', 'daar']]);
    heap.verify_heaps_law(blacklab_url,total_sentences=5000,sample_percentage=None,outputFile="Data/small_sample_heap.pdf")
