import random
import time
from deap import base, creator
from deap import tools
from json import load
from lib_ga import *

jsonFile = "bd.json"
with open(jsonFile) as f:
    instance = load(f)
depot = instance["depot"]


'#Parâmetros Iniciais'
IND_SIZE = 21
nGen = 100
cxPb = 0.5
mutPb = 0.1
size = 3200

creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0,))
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()
toolbox.register("genotipo", random.sample, range(1, 22), IND_SIZE)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.genotipo)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate, instance=instance, size=size)
toolbox.register("select", tools.selTournament)
toolbox.register("mutate", mutate)
toolbox.register("mate", pmxCrossover)


if __name__ == "__main__":

    start = time.process_time()
    pop = toolbox.population(100)

    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # Inicio da evolução
    for g in range(nGen):
        print("------- Generation %s -------" %(g+1))
        offspring = toolbox.select(pop, len(pop), 2)
        offspring = list(map(toolbox.clone, offspring))

        # Aplicando cruzamento nos descendentes
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.uniform(0, 1) < cxPb:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        #Aplicando mutação nos descendentes
        for mutant in offspring:
            if random.uniform(0, 1) < mutPb:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalidInd = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalidInd)
        for ind, fit in zip(invalidInd, fitnesses):
            ind.fitness.values = fit
        tam = len(pop)
        pop[:] = offspring + pop #Colocando os filhos junto dos pais
        pop[:] = tools.selSPEA2(pop, tam) #Pegando os melhores dos pais e filhos
    qt = len(pop)
    indicesDesc = []
    indices = []
    for i in range(qt):
        for j in range(qt):
            if i != j:
                boolean = Similarity(pop[i], pop[j])
                if boolean is True:
                    indicesDesc.append(j)
                elif boolean is False and i not in indicesDesc and i not in indices:
                    indices.append(i)

    values = sorted(set(indices))
    print("Indíces de indivíduos únicos ou que se repetem: %s" %values)
    frontPareto = FastNonDominatedSort(pop, values)
    print("---- Fronte de Pareto ----")
    print("Posição 1: Genótipo")
    print("Posição 2: Soluções Dominadas")
    print("Posição 3: Soluções que a dominam")
    print("Posição 4: Aptidão(Distância, Qt. de Carros)")
    for ash in range(len(frontPareto)):
        print(frontPareto[ash])
    end = time.process_time()
    temp = (end - start)/60
    print("Duração do código em minutos: %s" %temp)




