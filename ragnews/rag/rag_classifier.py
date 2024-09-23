import re 

from db_wrapper.articledb import ArticleDB
from rag.rag_masked import rag_masked

class RAG_Classifier:
    def __init__(
            self, 
            labels_to_predict=[], 
            db_name="../sql_dbs/ragnews.db",
            llm_model="llama-3.1-70b-versatile",
            article_limit=5
        ):
        self.labels_to_predict = labels_to_predict
        self.db_name = db_name
        self.llm_model = llm_model
        self.article_limit = article_limit

    def find_labels_to_predict(self, text):
        '''
        >>> from evaluate import RAG_Classifier
        >>> model = RAG_Classifier()
        >>> model.find_labels_to_predict('[MASK0] is the democratic nominee [MASK1] is the republican nominee')
        ['[MASK0]', '[MASK1]']
        '''
        # Pattern to match [MASK] where 0 could be any digit
        pattern = r"\[MASK\d+\]"
        
        # Find all occurrences in the string
        matches = re.findall(pattern, text)
        
        return list(set(matches))
    
    def predict(self, x):
        '''
        >>> from evaluate import RAG_Classifier
        >>> model = RAGClassifier()
        >>> model.predict('There is no mask token here.')
        []
        >>> model.predict('[MASK0] is the democratic nominee')
        ['Harris']
        >>> model.predict('[MASK0] is the democratic nominee [MASK1] is the republican nominee')
        ['Harris', 'Trump']
        '''
        self.labels_to_predict = self.find_labels_to_predict(x)
        new_x = x
        predictions = []
        for label in self.labels_to_predict:
            # keep on replacing predictions in x when found to always look for [MASK0]
            new_x = new_x.replace(label, "[MASK0]")
            db = ArticleDB(self.db_name)
            output = rag_masked(new_x, db, self.article_limit, self.llm_model)
            predictions += [output]
            new_x = new_x.replace("[MASK0]", output)
        return predictions