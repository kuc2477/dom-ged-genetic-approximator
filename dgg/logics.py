from bs4 import Tag
from .types import Step, DOMTree
from .utils import delta_sum


def dumb_deletion_steps_for(tree):
    return [Step(Step.D, i) for i in reversed(range(len(tree)))]


def dumb_creation_steps_for(tree):
    steps = []


def _dumb_creation_steps_for(node, steps=None):
    steps = steps or []

    for e in node.contents:
        if isinstance(element, Tag):
            delta = delta_sum(steps)
            step = Step(Step.A, delta_sum(steps))
            tag = soup.new_tag(element.name, delta_sum(steps), **element.attrs)
        else:
            tag = str(element)
