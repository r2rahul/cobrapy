from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, Query
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy import create_engine, Column, String, Float, ForeignKey

from numpy import array
from scipy.sparse import dok_matrix

Base = declarative_base()
Session = sessionmaker()

class Reaction(Base):
    __tablename__ = "reactions"
    id = Column(String(200), primary_key=True)
    lower_bound = Column(Float)
    upper_bound = Column(Float)
    subsystem = Column(String(200))
    objective_coefficient = Column(Float)
    variable_kind = Column(String(20), default="continuous")
    # the reaction_metabolites are indexed by metabolite
    _reaction_metabolites = relationship("_ReactionMetabolites",
        backref="reaction",
        collection_class=attribute_mapped_collection("metabolite"))
    # the metabolites are a dict. The values will be the stoichiometry of
    # the reaction_metabolite. The values are already indexed by
    # the metabolite
    metabolites = association_proxy("_reaction_metabolites", "stoichiometry",
        creator=lambda metabolite, stoichiometry:  # key is metabolite
            _ReactionMetabolites(stoichiometry=stoichiometry,
                                metabolite=metabolite))
    @property
    def _metabolites(self):
        # TODO warn
        return self.metabolites

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise ValueError("too many arguments")
        if len(args) == 1:
            if "id" in kwargs:
                raise ValueError("id specified by both arg and kwarg")
            kwargs["id"] = args[0]
        Base.__init__(self, **kwargs)

    def add_metabolites(self, metabolite_dict):
        self.metabolites.update(metabolite_dict)

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self)
    
    def parse_gene_association(self):
        return None

class Metabolite(Base):
    __tablename__ = "metabolites"
    id = Column(String(200), primary_key=True)
    _reaction_metabolites = relationship("_ReactionMetabolites",
        backref="metabolite")
    #formula = Column(String(400))
    _constraint_sense = Column(String(1), default="E")
    _bound = Column(Float, default=0.)
    reactions = relationship(Reaction,
        secondary=lambda: _ReactionMetabolites.__table__, viewonly=True)
    
    @property
    def _reaction(self):
        # TODO warn
        return self.reactions
    
    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self)

class _ReactionMetabolites(Base):
    __tablename__ = "reaction_metabolites"
    reaction_id = Column(String(200),
        ForeignKey("reactions.id"), primary_key=True)
    metabolite_id = Column(String(200),
        ForeignKey("metabolites.id"), primary_key=True)
    stoichiometry = Column(Float)
    def __repr__(self):
        return "(%s, %s) %f" % \
            (self.reaction_id, self.metabolite_id, self.stoichiometry)
           
class QueryList:
    def __init__(self, model, obj):
        self._model = model
        self.query = self._model.query(obj).order_by(obj.id.asc())
        for i in ["all", "__getitem__", "__iter__"]:
            setattr(self, i, getattr(self.query, i))
        self.__len__ = self.query.count
    def get_by_id(self, id):
        result = self.query.filter_by(id=str(id)).one()
        if result is not None:
            return result
        else:
            raise KeyError("id %s")
        

class Model(Session):
    def __init__(self, id="", engine=None):
        if engine is None:
            engine = create_engine('sqlite:///:memory:', echo=False)
            Base.metadata.create_all(engine)
        super(Model, self).__init__(bind=engine)
        self.engine = engine
        self.reactions = QueryList(self, Reaction)
        self.metabolites = QueryList(self, Metabolite)
    def add_reaction(self, reaction):
        self.add(reaction)
        self.commit()
    def add_reactions(self, reaction_list):
        super(Model, self).add_all(reaction_list)
        self.commit()
    def __getstate__(self):
        objects = {}
        objects["reactions"] = self.query(Reaction.id, Reaction.lower_bound,
            Reaction.upper_bound, Reaction.objective_coefficient,
            Reaction.subsystem, Reaction.variable_kind).all()
        objects["metabolites"] = self.query(Metabolite.id, Metabolite._bound,
            Metabolite._constraint_sense).all()
        objects["stoichiometry"] = self.query(_ReactionMetabolites.reaction_id,
            _ReactionMetabolites.metabolite_id,
            _ReactionMetabolites.stoichiometry).all()
        return objects

    def __setstate__(self, objects):
        self.__init__()
        reactions = [Reaction(id=i[0], lower_bound=i[1], upper_bound=i[2],
            objective_coefficient=i[3], subsystem=i[4], variable_kind=i[5])
            for i in objects["reactions"]]
        metabolites = [Metabolite(id=i[0], _bound=i[1], _constraint_sense=i[2])
            for i in objects["metabolites"]]
        stoichiometry = [_ReactionMetabolites(reaction_id=i[0],
            metabolite_id=i[1], stoichiometry=i[2])
            for i in objects["stoichiometry"]]
        self.add_all(reactions)
        self.add_all(metabolites)
        self.add_all(stoichiometry)

if __name__ == "__main__":
    model1 = Model()
    rxn1 = Reaction(id="test_reaction")
    rxn2 = Reaction(id="test_reaction2")
    met1 = Metabolite(id="met1")
    met2 = Metabolite(id="met2")
    rxn1.metabolites[met1] = 1
    rxn1.metabolites[met2] = -1
    rxn2.metabolites[met1] = 1
    model1.add_all([rxn1, rxn2])
    model1.commit()
    model2 = Model()
    model = model1
    #print model1.metabolites.all()

    from IPython import embed
    embed()
