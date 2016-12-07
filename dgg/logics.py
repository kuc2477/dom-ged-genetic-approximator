import copy
from bs4 import BeautifulSoup, Tag, NavigableString
from .types import Step, DOMTree
from .utils import delta_sum


def dumb_deletion_steps_for(tree):
    return [Step(Step.D, i) for i in reversed(range(len(tree)))]


def dumb_creation_steps_for(tree):
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

        if isinstance(e, Tag):
            step = Step(Step.A, parent_index, name=e.name, attrs=e.attrs)
        else:
            step = Step(Step.A, parent_index, content=str(e))

        steps.append(step)

    return steps
