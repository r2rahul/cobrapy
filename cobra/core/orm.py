from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, Query
from sqlalchemy.orm import object_session
from sqlalchemy import event
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy import create_engine, Column, String, Float, ForeignKey

from numpy import array
from scipy.sparse import dok_matrix

from warnings import warn

Base = declarative_base()
Session = sessionmaker()

@event.listens_for(Session, "after_attach")
def _on_session_add(session, instance):
    if hasattr(instance, "_on_session_add"):
        instance._update_gene_mapping()

# Because sqlite does not do ON UPDATE CASCADE, it needs this to be false.
# However, on other databases, setting this to False incurs a performance
# penalty and should be set to True. 
_passive_updates = False

class Gene(Base):
    __tablename__ = "genes"
    id = Column(String(30), primary_key=True)
    
    def __str__(self):
        return "Gene " + self.id
    
    def __repr__(self):
        return str(self)

class _ReactionGenes(Base):
    __tablename__ = "reaction_genes"
    reaction_id = Column(String(200),
        ForeignKey("reactions.id"), primary_key=True)
    gene_id = Column(String(30),
        ForeignKey("genes.id"), primary_key=True)

class Reaction(Base):
    __tablename__ = "reactions"
    id = Column(String(200), primary_key=True)
    name = Column(String(200))
    subsystem = Column(String(200))

    lower_bound = Column(Float, default=-1000.)
    upper_bound = Column(Float, default=1000.)
    objective_coefficient = Column(Float, default=0.)
    variable_kind = Column(String(20), default="continuous")
    
    # to populate the many to many relationship between genes and reactions,
    # we need to use a setter and a getter for the gene_reaction_rule attribute
    _gene_reaction_rule = Column("gene_reaction_rule", String(200))
    genes = relationship(Gene,
        secondary=_ReactionGenes.__table__, viewonly=True,
        backref=backref("reactions", viewonly=True))
    # can be appended to
    _genes = relationship(Gene, secondary=_ReactionGenes.__table__)
    
    @property  # should this be hybrid_property?
    def gene_reaction_rule(self):
        return self._gene_reaction_rule
    
    @gene_reaction_rule.setter
    def gene_reaction_rule(self, rule):
        self._gene_reaction_rule = rule
        # If the object is associated with a session update the mapping. If
        # not, the listener will handle it after it is attached to one
        if object_session(self) is not None:
            self._update_gene_mapping()

    def _on_session_add(session, instance):
        instance._update_gene_mapping()

    def _update_gene_mapping(self):
        """populate _ReactionGenes appropriately given gene_reaction_rule"""
        self._genes = []
        list_string = self._gene_reaction_rule
        if list_string is None:
            return
        if len(list_string) == 0:
            return
        # replacement is faster than regular expression, which would be
        # re.compile("(and)|(or)|\(|\)", re.IGNORECASE)
        list_string = list_string.replace("and", "")
        list_string = list_string.replace("AND", " ")
        list_string = list_string.replace("or", " ")
        list_string = list_string.replace("OR", " ")
        list_string = list_string.replace("(", " ")
        list_string = list_string.replace(")", " ")
        session = object_session(self)
        for gene_id in set(list_string.split()):
            new_gene = session.query(Gene).filter_by(id=gene_id).first()
            if new_gene is None:
                new_gene = Gene(id=gene_id)
            self._genes.append(new_gene)
    
    # the reaction_metabolites are indexed by metabolite
    _reaction_metabolites = relationship("_ReactionMetabolites",
        backref="reaction",
        passive_updates=_passive_updates,
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
        warn("deprecated call to _metabolites")
        return self.metabolites

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError("Too many arguments supplied")
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
    
    def reconstruct_reaction(self): warn("depracated")

    @property
    def reaction(self):
        """Generate a human readable reaction string."""
        reactant_dict = {}
        product_dict = {}
        def coefficient_to_string(number):
            if number == 1:
                return ""
            if number == int(number):
                return str(int(number)) + " "
            return "%.2f " % number
        for metabolite, coefficient in self.metabolites.items():
            id = metabolite.id
            if coefficient > 0:
                product_dict[id] = coefficient_to_string(coefficient)
            else:
                reactant_dict[id] = coefficient_to_string(abs(coefficient))
        reactant_string = " + ".join(['%s%s' % (coefficient_str, metabolite) for metabolite, coefficient_str in reactant_dict.items()])
        if self.upper_bound <= 0:
            arrow = ' <- '
        elif self.lower_bound >= 0:
            arrow = ' -> '                
        else:
            arrow = ' <=> '
        product_string = " + ".join(['%s%s' % (coefficient_str, metabolite) for metabolite, coefficient_str in product_dict.items()])
        reaction_string = reactant_string + arrow + product_string
        return reaction_string


class Metabolite(Base):
    __tablename__ = "metabolites"
    id = Column(String(200), primary_key=True)
    _reaction_metabolites = relationship("_ReactionMetabolites",
        passive_updates=_passive_updates,
        backref="metabolite")
    #formula = Column(String(400))
    _constraint_sense = Column(String(1), default="E")
    _bound = Column(Float, default=0.)
    reactions = relationship(Reaction,
        secondary=lambda: _ReactionMetabolites.__table__, viewonly=True)

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError("Too many arguments supplied")
        if len(args) == 1:
            if "id" in kwargs:
                raise ValueError("id specified by both arg and kwarg")
            kwargs["id"] = args[0]
        Base.__init__(self, **kwargs)
    
    @property
    def _reaction(self):
        warn("deprecated call to _reactions")
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

           
class QueryList(object):
    def __init__(self, model, obj):
        self._model = model
        self._obj = obj
        self.query = self._model.query(obj).order_by(obj.id.desc())
        
        for i in ["all", "__iter__"]:
            setattr(self, i, getattr(self.query, i))
        self.__len__ = self.query.count
        # create functions to get all attributes of the given class

    def list_attr(self, attribute):
        warn("depracated call to list_attr")
        return self._model.query(getattr(self._obj, attribute)).order_by(self._obj.id.desc()).all()

    def get_by_id(self, id):
        """return an object by its id"""
        result = self.query.get(str(id))
        if result is not None:
            return result
        else:
            raise KeyError("id %s" % id)
    
    def __getitem__(self, key):
        if type(key) is int:
            return self.query[key]
        else:
            return self.query.get(key)

    def __dir__(self):
        attributes = self.__class__.__dict__.keys()
        attributes.extend([i[0] for i in self._model.query(self._obj.id).all()])
        return attributes

    def __getattr__(self, attr):
        try:
            return super(QueryList, self).__getattribute__(attr)
        except:
            query = super(QueryList, self).__getattribute__("query")
            result = query.get(attr)
            if result is not None:
                return result
            else:
                raise AttributeError("Item %s not found" % (attr))

    def _generate_index(self):
        warn("depracated call to _generate_index")


class Model:
    def __init__(self, id="", engine=None):
        if engine is None:
            engine = create_engine('sqlite:///:memory:', echo=False)
            Base.metadata.create_all(engine)
        self.session = Session(bind=engine)
        self.engine = engine
        # add relevant functions from session
        for attr in ["add", "add_all", "query", "commit"]:
            setattr(self, attr, getattr(self.session, attr))

        self.reactions = QueryList(self, Reaction)
        self.metabolites = QueryList(self, Metabolite)
        self.genes = QueryList(self, Gene)

    def add_reaction(self, reaction):
        self.session.add(reaction)
        self.session.commit()

    def add_reactions(self, reaction_list):
        self.session.add_all(reaction_list)
        self.commit()

    def __getstate__(self):
        objects = {}
        objects["reactions"] = self.session.query(Reaction.id, Reaction.lower_bound,
            Reaction.upper_bound, Reaction.objective_coefficient,
            Reaction.subsystem, Reaction.variable_kind, Reaction._gene_reaction_rule).all()
        objects["metabolites"] = self.session.query(Metabolite.id, Metabolite._bound,
            Metabolite._constraint_sense).all()
        objects["stoichiometry"] = self.session.query(_ReactionMetabolites.reaction_id,
            _ReactionMetabolites.metabolite_id,
            _ReactionMetabolites.stoichiometry).all()
        return objects

    def __setstate__(self, objects):
        self.__init__()
        # adding gprs makes this super slow - TODO speedup
        self.add_all((Reaction(id=i[0], lower_bound=i[1], upper_bound=i[2],
            objective_coefficient=i[3], subsystem=i[4], variable_kind=i[5], _gene_reaction_rule=i[6])
            for i in objects["reactions"]))
        metabolites = [Metabolite(id=i[0], _bound=i[1], _constraint_sense=i[2])
            for i in objects["metabolites"]]
        stoichiometry = [_ReactionMetabolites(reaction_id=i[0],
            metabolite_id=i[1], stoichiometry=i[2])
            for i in objects["stoichiometry"]]
        self.add_all(metabolites)
        self.add_all(stoichiometry)

    def cache(self):
        """access all attributes to cause them to get cached in memory"""
        self.reactions.all()
        self.metabolites.all()
        for i in self.reactions:
            i.metabolites
        for i in self.metabolites:
            i.reactions
        


if __name__ == "__main__":
    model1 = Model()
    rxn1 = Reaction(id="test_reaction")
    rxn2 = Reaction(id="test_reaction2")
    met1 = Metabolite(id="met1")
    met2 = Metabolite(id="met2")
    #rxn1.metabolites[met1] = 1
    rxn1.add_metabolites({met1: 1})
    rxn1.metabolites[met2] = -1
    rxn2.metabolites[met1] = 1
    model1.add_all([rxn1, rxn2])
    model1.commit()
    model2 = Model()
    model = model1
    #print model1.metabolites.all()

    from IPython import embed
    embed()
