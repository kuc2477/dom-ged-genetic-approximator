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
        self.__validate(type, target, name, content, attrs)
        self.type = type
        self.target = target
        self.name = name
        self.content = content
        self.attrs = attrs or {}

    @property
    def delta(self):
        if self.type in (Step.W, Step.A):
            return 1
        elif self.type == Step.D:
            return -1
        else:
            return 0

    @classmethod
    def __validate(self, type, target, name=None, content=None, attrs=None):
        if type not in Step.TYPES:
            raise TypeError('Invalid step type: {}'.format(type))
        if type ==Step.W and not name:
            raise ValueError('Wrap step requires tag name')
        if type == Step.A and (not name and not content):
            raise ValueError((
                'Append step should contain at least one of tag '
                'name or content'
            ))
        if type == Step.M and (not name and not content and not attrs):
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


class DOMTree(object):
    def __init__(self, html):
        self._soup = clean_soup(BeautifulSoup(html, 'html.parser'))
        self._steps_applied = []
        self._nodes_applied = []
        self._cache = {}
        self._cache_validities = {}

    def step_forward(self, step):
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
        current.append(tag)
        return previous

    def _delete(self, step):
        current = self._get_tag(step.target)
        previous = copy.deepcopy(current)
        # unwrap if the target has any children.
        if isinstance(current, Tag) and current.contents:
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

    def _all_tag_names(self):
        return {t.name for t in self.descendants if t.name}

    def _all_attributes(self, name):
        # TODO: NOT IMPLEMENTED YET
        pass

    def _all_contents(self, name):
        # TODO: NOT IMPLEMENTED YET
        pass

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
