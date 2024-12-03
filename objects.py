class RetrievalTestingOutput:
    def __init__(self, topicID, docno, rank, score, runTag = "j29parmaAND", Q = "Q0"):
        self.topicID = topicID
        self.docno = docno
        self.rank = rank
        self.score = score
        self.runTag = runTag
        self.Q = Q

class RetrievalOutput:
    def __init__(self, rank, headline, date, docno, query_biased_snippet=None):
        self.rank = rank
        self.headline = headline
        self.date = date
        self.docno = docno
        self.query_biased_snippet = query_biased_snippet
    
    def add_snippet(self, snippet):
        self.query_biased_snippet = snippet
    