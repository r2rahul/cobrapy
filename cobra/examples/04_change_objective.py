# cobra/examples/04_change_objective_example.py
# This example changes the targeted objective for the optimization function.

#Load in the example model file
from cobra.test import create_test_model, salmonella_pickle  # test filename

cobra_model = create_test_model(salmonella_pickle)

cobra_model.optimize()
print 'solution for old objective (should be approximately 0.32):'
print cobra_model.solution.f

my_objective = cobra_model.reactions.get_by_id('3OAS140')
print 'Changing objective to %s'%my_objective.id
cobra_model.optimize(new_objective=my_objective)
print 'solution for %s (should be approximately 2.5):'%my_objective.id
print cobra_model.solution.f

