class BaseScorer:
    # To handle errors
    def score(self,lead):
        raise NotImplementedError("Subclass must implement score()")
    
class RuleBaseScorer(BaseScorer):
    def score(self, lead):
        points = 0
        if lead.website:
            points += 15

        if lead.description:
            points += 10
        
        if lead.google_rating > 4.5:
            points += 20
        
        elif 2.5 <= lead.google_rating < 4.5:
            points += 10

        elif 1.5 <= lead.google_rating < 2.5:
            points += 5
        
        elif 0 <= lead.google_rating < 1.5:
            points -= 5

        if lead.review_count >= 15:
            points += 20
        
        elif 10 <= lead.review_count < 15:
            points += 15
        
        elif 5 <= lead.review_count < 10:
            points += 10

        elif 0 <= lead.review_count < 5:
            points += 5

        lead.score = points

        return lead
    

