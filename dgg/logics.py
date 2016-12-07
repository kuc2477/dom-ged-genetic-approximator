from .types import Step, DOMTree


def create_dumb_steps(tree_from, tree_to):
    steps = []

    # delete all nodes
    for i in reversed(range(len(tree_from))):
        steps.append(Step(Step.D, i))

    return steps
