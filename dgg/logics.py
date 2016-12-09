import itertools
import random
import copy
from bs4 import BeautifulSoup, Tag, NavigableString
from deap import tools
from .types import Step, Sequence, DOMTree
from .utils import delta_sum


# ===============
# Initializations
# ===============

def dumb_sequence_for(tree_from ,tree_to):
    return Sequence(
        _dumb_deletion_steps_for(tree_from) +
        _dumb_creation_steps_for(tree_to)
    )


def _dumb_deletion_steps_for(tree):
    return [Step(Step.D, i) for i in reversed(range(len(tree)))]


def _dumb_creation_steps_for(tree):
    soup = copy.copy(tree.soup)
    steps = []

    for i, e in enumerate(soup.descendants):
        e.__index__ = i

    for i, e in enumerate(soup.descendants):
        # get index of parent element. we consider element's parent as soup
        # if it's parent has no index.
        try:
            parent_index = e.parent.__index__
        except AttributeError:
            parent_index = -1
        # create step depending on the element's type.
        if isinstance(e, Tag):
            step = Step(Step.A, parent_index, name=e.name, attrs=e.attrs)
        else:
            step = Step(Step.A, parent_index, content=str(e))
        # append new step to the sequence.
        steps.append(step)

    return steps


def sequences_from_dumb_sequence(dumb_sequence, n=100, 
                                 feature_mutation_pb=0.5, 
                                 type_mutation_pb=0.5,
                                 target_mutation_mu=0, 
                                 target_mutation_sigma=1):
    if n < 1: 
        raise ValueError('n has to be either equal or larger than 1')
    sequences = [dumb_sequence]
    for _ in range(n - 1):
        mutant = copy.deepcopy(dumb_sequence)
        mutant = mutate(
            mutant, 
            feature_mutation_pb=feature_mutation_pb, 
            type_mutation_pb=type_mutation_pb, 
            target_mutation_mu=target_mutation_mu, 
            target_mutation_sigma=target_mutation_sigma,
        )
        sequences.append(mutant)
    return sequences

# =======================
# Evolutionary Operations
# =======================

def crossover(seq1, seq2):
    size = min(len(seq1), len(seq2))
    cxpoint = random.randint(1, size - 1)
    seq1[cxpoint:], seq2[cxpoint:] = seq1[cxpoint:], seq2[cxpoint:]
    return seq1, seq2


def mutate(seq, 
           feature_mutation_pb=0.5, 
           type_mutation_pb=0.5,
           target_mutation_mu=0, 
           target_mutation_sigma=1):
    mutate_features(seq, pb=feature_mutation_pb)
    mutate_types(seq, pb=type_mutation_pb)
    mutate_targets(seq, mu=target_mutation_mu, sigma=target_mutation_sigma)
    return seq


def mutate_features(seq, pb):
    features = [(s.name, s.content, s.attrs) for s in seq]
    mutated_features = tools.mutShuffleIndexes(features, pb)[0]
    for step, mutated_feature in zip(seq, mutated_features):
        # Note that we don't validate every step after the feature mutation.
        # Instead, step validation should be done in type mutation which will
        # be done after the feature mutations.
        name, content, attrs = mutated_feature
        step.name = name
        step.content = content
        step.attrs = attrs
    return seq


def mutate_types(seq, pb):
    for step in seq:
        for type in tools.mutShuffleIndexes(list(Step.TYPES), pb)[0]:
            try:
                step.type = type
                step.validate()
            except (TypeError, ValueError):
                continue
            else:
                break
    return seq


def mutate_targets(seq, mu=0, sigma=1):
    for step in seq:
        step.target += random.normalvariate(mu, sigma)
        step.target = int(step.target)
    return seq


def select(sequences, tree_from, tree_to):
    # TODO: NOT IMPLEMENTED YET
    pass
