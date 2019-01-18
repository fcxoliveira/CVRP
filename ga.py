import random
import time
from deap import base, creator
from deap import tools
from json import load

jsonFile = "bd.json"
with open(jsonFile) as f:
    instance = load(f)
depot = instance["depot"]


def evaluate(ind, instance, size):
    distance = 0
    demand = 0
    vehicles = 0
    keyAnt = "depot"
    for i in range(len(ind)):

        demandCustomer = instance["c" + str(ind[i])]["demand"]

        if i == len(ind) - 1:
            vehicles += 1
            distance += instance["c" + str(keyAnt)]["distance"][str(ind[i])]

        elif demand + demandCustomer > size:
            vehicles += 1
            demand = demandCustomer
            distance += instance["depot"]["distance"][str(ind[i])]

        elif demand + demandCustomer == size:
            vehicles += 1
            demand = 0
            distance += instance["c" + str(keyAnt)]["distance"][str(ind[i])]

        elif demand + demandCustomer < size:
            if i == 0:
                distance = instance["depot"]["distance"][str(ind[i])]
            else:
                distance += instance["c" + str(keyAnt)]["distance"][str(ind[i])]
            demand += demandCustomer
        keyAnt = str(ind[i])

    return distance, vehicles  # minimizar a distância e o número de veiculos


def mutate(individual):
    indmutate = individual
    chance = random.uniform(0, 1)

    swap1 = random.randint(1, 21) - 1
    swap2 = swap1
    while swap2 == swap1:
        swap2 = random.randint(1, 21) - 1
    aux = indmutate[swap1]
    indmutate[swap1] = indmutate[swap2]
    indmutate[swap2] = aux
    return indmutate

def _repeated(element, collection):
    c = 0
    for e in collection:
        if e == element:
            c += 1
    return c > 1


def _swap(data_a, data_b, cross_points):
    c1, c2 = cross_points
    new_a = data_a[:c1] + data_b[c1:c2] + data_a[c2:]
    new_b = data_b[:c1] + data_a[c1:c2] + data_b[c2:]
    return new_a, new_b


def _map(swapped, cross_points):
    n = len(swapped[0])
    c1, c2 = cross_points
    s1, s2 = swapped
    map_ = s1[c1:c2], s2[c1:c2]
    for i_chromosome in range(n):
        if not c1 < i_chromosome < c2:
            for i_son in range(2):
                while _repeated(swapped[i_son][i_chromosome], swapped[i_son]):
                    map_index = map_[i_son].index(swapped[i_son][i_chromosome])
                    swapped[i_son][i_chromosome] = map_[1 - i_son][map_index]
    return s1, s2


def pmxCrossover(parent_a, parent_b):
    assert (len(parent_a) == len(parent_b))
    n = len(parent_a)
    cross_points = sorted([random.randint(0, n) for _ in range(2)])
    swapped = _swap(parent_a, parent_b, cross_points)
    mapped = _map(swapped, cross_points)
    return mapped


def Similarity(ind1, ind2):
    c = 0
    t = len(ind1)
    for i in range(t):
        if ind1[i] == ind2[i]:
            c += 1
    return t - c == 0


def FastNonDominatedSort(pop, values):
    generation = []
    for pos1 in values:
        dominated = 0
        dominates_me = 0
        si = pop[pos1]
        for pos2 in values:
            sj = pop[pos2]
            if pos1 != pos2:
                distance1 = si.fitness.values[0]
                distance2 = sj.fitness.values[0]
                numCars1 = si.fitness.values[1]
                numCars2 = sj.fitness.values[1]
                if numCars1 < numCars2 and distance1 <= distance2:
                    dominated += 1
                elif numCars1 == numCars2 and distance1 < distance2:
                    dominated += 1
                elif numCars2 < numCars1 and distance2 <= distance1:
                    dominates_me += 1
                elif numCars2 == numCars1 and distance2 < distance1:
                    dominates_me += 1
        temp = [si, dominated, dominates_me, si.fitness.values]
        generation.append(temp)
    generation_non_dominate = []
    for p in range(len(generation)):
        ind = generation[p]
        if ind[2] == 0:
            generation_non_dominate.append(ind)
    return generation_non_dominate

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
    print(values)
    frontPareto = FastNonDominatedSort(pop, values)
    for ash in range(len(frontPareto)):
        print(frontPareto[ash])
    end = time.process_time()
    temp = (end - start)/60
    print(temp)
