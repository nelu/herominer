from app.game.heroes.stats import StatusData


class Ascension(StatusData):
    def __init__(self, self1):
        super().__init__()
        self.rank = 1
        self.role_specialization = None

    def upgrade_rank(self):
        self.rank += 1

    def specialize_role(self, role):
        self.role_specialization = role

    def to_dict(self):
        return {'rank': self.rank, 'role_specialization': self.role_specialization}
