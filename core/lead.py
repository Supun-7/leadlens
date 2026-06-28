class Lead:

    def __init__(self, name, website, description, location):
        self.name = name
        self.website = website
        self.description = description
        self.location = location
        self.score = 0
        self.notes = []

    def to_dict(self):
        return{
            "name": self.name,
            "website": self.website,
            "description": self.description,
            "location":self.location,
            "score": self.score,
            "notes": self.notes
        }

