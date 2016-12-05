import random
from deap import base, creator, tools, algorithms


POPULATION_SIZE = 300
GENE_SIZE = 100
GENERATION_NUM = 50
DISPLAY_BEST_K = 2


if __name__ == '__main__':
    creator.create('FitnessMin', base.Fitness, weights=(1.0,))
    creator.create('Individual', list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register('boolean_attribute', random.randint, 0, 1)
    toolbox.register(
        'individual', tools.initRepeat, 
        creator.Individual, toolbox.boolean_attribute, n=GENE_SIZE,
    )
    toolbox.register('population', tools.initRepeat, list, toolbox.individual)
    toolbox.register('evaluate', lambda individual: sum(individual))
    toolbox.register('mate', tools.cxTwoPoint)
    toolbox.register('mutate', tools.mutFlipBit, indpb=0.05)
    toolbox.register('select', tools.selTournament, tournsize=3)

    # initialize first generation
    population = toolbox.population(n=POPULATION_SIZE)
    for individual in population:
        individual.fitness.values = (toolbox.evaluate(individual),)

    for gen in range(GENERATION_NUM):
        # display current generation's statistics
        print('generation {}'.format(gen))
        print('top{}: {}'.format(
            DISPLAY_BEST_K,
            list(map(
                lambda i: i.fitness.values,
                tools.selBest(population, k=DISPLAY_BEST_K)
            ))
        ))

        # generate next generation
        offsprings = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
        fitnesses = toolbox.map(toolbox.evaluate, offsprings)
        for fitness, individual in zip(fitnesses, offsprings):
            individual.fitness.values = [fitness]
        population = toolbox.select(offsprings, k=len(population))

    # display last generation's statistics
    print('\n\n')
    print('top{}: {}'.format(
        DISPLAY_BEST_K,
        list(map(
            lambda i: i.fitness.values,
            tools.selBest(population, k=DISPLAY_BEST_K)
        ))
    ))
