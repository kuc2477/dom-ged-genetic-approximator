import random
import copy
from bs4 import BeautifulSoup, NavigableString, Tag
from .utils import clean_soup


class Step(object):
    W = WRAP = 'W'
    A = APPEND = 'A'
    D = DELETE = 'D'
    M = MODIFY = 'M'
    TYPES = (W, A, D, M)

    def __init__(self, type, target, name=None, content=None, attrs=None):
        self.type = type
        self.target = target
        self.name = name
        self.content = content
        self.attrs = attrs or {}
        # validate the step.
        self.validate()

    @property
    def delta(self):
        if self.type in (Step.W, Step.A):
            return 1
        elif self.type == Step.D:
            return -1
        else:
            return 0

    def validate(self):
        if self.type not in Step.TYPES:
            raise TypeError('Invalid step type: {}'.format(type))
        if self.type ==Step.W and not self.name:
            raise ValueError('Wrap step requires tag name')
        if self.type == Step.A and (not self.name and not self.content):
            raise ValueError((
                'Append step should contain at least one of tag '
                'name or content'
            ))
        if self.type == Step.M and (
                not self.name and 
                not self.content and 
                not self.attrs):
            raise ValueError((
                'Modify step should contain at least one of tag name, content '
                'or attrs'
            ))

    def __str__(self):
        if self.type == Step.W:
            return '{}{}[{}][{}]'.format(
                self.type,
                self.target,
                self.name,
                self.attrs,
            )
        elif self.type in (Step.A, Step.M):
            # truncate some contents for your eyes
            if self.content and len(self.content) > 10:
                truncated = repr(self.content[:10].strip() + '..')
            elif self.content:
                truncated = repr(self.content)
            else:
                truncated = ''

            return '{}{}[{}][{}][{}]'.format(
                self.type, self.target, self.name, 
                truncated, self.attrs,
            )
        else:
            return '{}{}'.format(self.type, self.target)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self.type != other.type:
            return False

        if self.type in (Step.A, Step.M):
            return self.target == other.target and \
                self.name == other.name and \
                self.content == other.content and \
                self.attrs == other.attrs
        else:
            return True


class Sequence(object):
    __cache = {}

    def __init__(self, steps=None):
        self._steps = steps or []
        self._fitness = None

    @property
    def steps(self):
        return self._steps

    @property
    def fitness(self):
        return self._fitness

    def evaluate(self, html_from, html_to, base=None):
        cache = self.__cache

        # use tree from cache rather than parsing entire html
        if html_from in cache:
            tree_from = copy.deepcopy(cache[html_from])
        else:
            tree_from = DOMTree(html_from)
            cache[html_from] = copy.deepcopy(tree_from)

        # use tree from cache rather than parsing entire html
        if html_to in cache:
            tree_to = copy.deepcopy(cache[html_to])
        else:
            tree_to = DOMTree(html_to)
            cache[html_to] = copy.deepcopy(tree_to)

        for step in self.steps:
            tree_from.run(step)

        # calculate sequence's fitness based on it's length
        if tree_from == tree_to:
            fitness = len(base) / len(self) if base else 1
        else:
            fitness = 0

        self._fitness = fitness
        return self._fitness

    def append(self, step):
        self.steps.append(step)
        self._fitness = None

    def pop(self):
        self.steps.pop()
        self._fitness = None

    def __iter__(self):
        self.__index = 0
        return self

    def __next__(self):
        if self.__index >= len(self.steps):
            raise StopIteration
        element = self.steps[self.__index]
        self.__index += 1
        return element

    def __getitem__(self, key):
        return self.steps[key]

    def __setitem__(self, key, data):
        self.steps[key] = data

    def __delitem__(self, key):
        del self.steps[key]

    def __add__(self, other):
        return self.steps + other

    def __mul__(self, other):
        return self.steps * other

    def __repr__(self):
        return repr(self.steps)

    def __str__(self):
        return str(self.steps)

    def __len__(self):
        return len(self.steps)


class DOMTree(object):
    def __init__(self, html):
        self._soup = clean_soup(BeautifulSoup(html, 'html.parser'))
        self._steps_applied = []
        self._nodes_applied = []
        self._cache = {}
        self._cache_validities = {}

    def run(self, step):
        if not len(self) and step.type != Step.A:
            return

        if step.type == Step.W:
            node_applied = self._wrap(step)
        elif step.type == Step.A:
            node_applied = self._append(step)
        elif step.type == Step.M:
            node_applied = self._modify(step)
        else:
            node_applied = self._delete(step)

        # record the step and applied node
        self._steps_applied.append(step)
        self._nodes_applied.append(node_applied)
        self._invalidate_cache('descendants')
        return self

    def run_sequence(self, seq):
        for step in seq:
            self.run(step)
        return self

    @property
    def soup(self):
        return self._soup

    @property
    def descendants(self):
        cache = self._get_cache('descendants')
        if cache:
            return cache
        else:
            descendants = list(self._soup.descendants)
            self._set_cache('descendants', descendants)
            return descendants

    @property
    def steps_applied(self):
        return self._steps_applied

    @property
    def nodes_applied(self):
        return self._nodes_applied

    def _wrap(self, step):
        tag = self._new_tag(step)
        current = self._get_tag(step.target)
        previous = copy.deepcopy(current)
        current.wrap(tag)
        return previous

    def _append(self, step):
        tag = self._new_tag(step)
        current = self._get_tag(step.target)
        previous = copy.deepcopy(current)
        if isinstance(current, Tag):
            current.append(tag)
        else: 
            current.insert_after(tag)
        return previous

    def _delete(self, step):
        current = self._get_tag(step.target)
        previous = copy.deepcopy(current)
        # unwrap if the target has any children.
        if isinstance(current, Tag) and current.contents and current.parent:
            current.unwrap()
        # otherwise extract the node.
        else:
            current.extract()
        return previous

    def _modify(self, step):
        current = self._get_tag(step.target)
        previous = copy.deepcopy(current)
        # modify attributes and tag name if the target has any children.
        if isinstance(current, Tag) and current.contents:
            current.name = step.name
            current.attrs = step.attrs
        # otherwise replace the entire target with new tag.
        else:
            tag = self._new_tag(step)
            current.replace_with(tag)
        return previous

    def _new_tag(self, step):
        if step.type not in (Step.W, Step.A, Step.M):
            raise TypeError('We can only make new tag for W, A and M step')

        # create new tag for the tree from the given step.
        if step.name:
            tag = self._soup.new_tag(step.name, **step.attrs)
            if step.content:
                tag.append(step.content)
        else:
            tag = NavigableString(step.content)
        return tag

    def _get_tag(self, target):
        # we clip target node on the maximum index.
        if target >= len(self):
            target = len(self) - 1
        try:
            return self.descendants[target]
        except IndexError:
            return self.soup

    def _get_cache(self, name):
        cache = self._cache.get(name)
        valid = self._cache_validities.get(name)
        if cache and valid:
            return cache
        else:
            return None

    def _set_cache(self, name, value):
        self._cache[name] = value
        self._cache_validities[name] = True

    def _invalidate_cache(self, name):
        self._cache_validities[name] = False

    def __str__(self):
        return self._soup.prettify()

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.descendants)

    def __eq__(self, other):
        return self.soup == other.soup
