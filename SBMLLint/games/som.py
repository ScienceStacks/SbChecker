"""Set of Molecules(SOM)."""

from SBMLLint.common import constants as cn
from SBMLLint.common.molecule import Molecule, MoleculeStoichiometry
from SBMLLint.common.reaction import Reaction
from SBMLLint.common.simple_sbml import SimpleSBML

from collections import deque

BRACKET_OPEN = "{"
BRACKET_CLOSE = "}"

class SOM(object):
    """
    The SOM (Set Of Molecules) class represents a collection of molecules
    each of which has equal weight. Consequently, the whole molecule space 
    can be partitioned into a collection of SOMs. The uni-uni reactions
    merge multiple SOM instances to create a larger one. 
    """
    soms = []  # All SOMs. 
    def __init__(self, molecules, reactions=set()):
        """
        :param set-Molecule molecules:
        :param set-Reaction reactions:
        """
        self.molecules = molecules
        self.reactions = reactions
        self.identifier = self.makeId()
        self.__class__.addSOM(self)

    def __repr__(self):
        return self.identifier        
        
    def makeId(self):
        """
        Creates an identifier for the SOM to uniquely
        identifies its elements.
        :return str:
        """
        def joinMoleculeNames(molecules):
          names = [m.name for m in molecules]
          names.sort()
          return ', '.join(names)
        #
        identifier = "%s%s%s" % (
            BRACKET_OPEN, 
            joinMoleculeNames(list(self.molecules)),
            BRACKET_CLOSE
            )
        return identifier
        
    @classmethod    
    def addSOM(cls, new_som):
        """
        Adds a new som to SOM.soms
        and skips if it already exists
        :param SOM new_som:
        """
        if any([new_som.molecules.intersection(som.molecules) for som in cls.soms]):
          pass
        else:
          cls.soms.append(new_som)
    
    @classmethod
    def findSOM(cls, molecule):
        """
        Finds the SOM that contains molecule
        and returns SOM
        :param Molecule molecule:
        :return SOM/None:
        """    
        for som in cls.soms:
            for mole in som.molecules:
                if mole.name == molecule.name:
                    return som
        return None

    @classmethod
    def merge(cls, reaction):
        """
        Merges two SOMs using a UniUni reaction 
        and updates cls.soms
        :param Reaction reaction:
        :return SOM:
        """ 
        if reaction.category != cn.REACTION_1_1:
            raise ValueError("Reaction must have category 1-1. Cannot do merge.")
        else:
            som1 = cls.findSOM(reaction.reactants[0].molecule)
            som2 = cls.findSOM(reaction.products[0].molecule)
            
            if som1 == som2:
                return som1
            else:
                new_molecules = som1.molecules.union(som2.molecules)
                new_reactions = som1.reactions.union(som2.reactions)
                new_reactions.add(reaction)
                cls.soms.remove(som1)
                cls.soms.remove(som2)
                new_som = SOM(new_molecules, new_reactions)
                return new_som
        
    @classmethod
    def reduce(cls, reaction):
        """
        Reduces reaction using existing cls.soms
        :param Reaction reaction:
        :return reaction/False:
        """        
        # flag that will show whether the reaction was reduced
        reduced = False

        if reaction.category != cn.REACTION_n_n:
            return reduced
        
        for som in cls.soms:
            reactants_in = deque([mole_tuple for mole_tuple in  
                            reaction.reactants if 
                            mole_tuple.molecule in som.molecules])
            reactants_out = [mole_tuple for mole_tuple in  
                            reaction.reactants if 
                            mole_tuple.molecule not in som.molecules]
            products_in = deque([mole_tuple for mole_tuple in  
                            reaction.products if 
                            mole_tuple.molecule in som.molecules])
            products_out = [mole_tuple for mole_tuple in  
                            reaction.products if 
                            mole_tuple.molecule not in som.molecules]

            while reactants_in and products_in:
                reactant = reactants_in[0]
                product = products_in[0]

                if reactant.stoichiometry > product.stoichiometry:
                    reactants_in[0] = MoleculeStoichiometry(reactant.molecule,
                                                              reactant.stoichiometry - product.stoichiometry)
                    products_in.popleft()

                elif reactant.stoichiometry < product.stoichiometry:
                    products_in[0] = MoleculeStoichiometry(product.molecule,
                                                              product.stoichiometry - reactant.stoichiometry)
                    reactants_in.popleft()
                else:
                    reactants_in.popleft()
                    products_in.popleft()

            reactants = list(reactants_in) + reactants_out
            products = list(products_in) + products_out
            
            if (len(reaction.reactants) > len(reactants)) | \
            (len(reaction.products) > len(products)):
                reduced = True
                reaction.reactants = reactants
                reaction.products = products
            
        if reduced:
            reaction.identifier = reaction.makeIdentifier()
            reaction.category = reaction._getCategory() 
            return reaction
        else:
            return reduced

    @classmethod
    def initialize(cls, molecules):
        """
        Creates single-set soms
        :param list-Molecule molecules:
        """
        cls.soms = []
        for mole in molecules:
            SOM({mole})
 
