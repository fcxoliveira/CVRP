import random

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
