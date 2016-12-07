import random
import copy
from bs4 import BeautifulSoup, NavigableString, Tag


class Step(object):
    W = WRAP = 'W'
    A = APPEND = 'A'
    D = DELETE = 'D'
    M = MODIFY = 'M'
    TYPES = (W, A, D, M)

    def __init__(self, type, target, name=None, content=None, attrs=None):
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

        self.type = type
        self.target = target
        self.name = name
        self.content = content
        self.attrs = attrs

    @property
    def delta(self):
        if self.type == Step.A:
            return 1
        elif self.type == Step.D:
            return -1
        else:
            return 0

    def __eq__(self, other):
        if self.type != other.type:
            return False

        if self.type in (Step.A, Step.M):
            return self.name == other.name and \
                self.content == other.content and \
                self.attrs == other.attrs
        else:
            return True

    def __mantissa(self, to=2):
        return int(self.target * (10 ** to))

    def __str__(self):
        if self.type == Step.W:
            return '{}{}[{}, {}]'.format(
                self.type,
                self.__mantissa(),
                self.name,
                self.attrs,
            )
        elif self.type in (Step.A, Step.M):
            return '{}{}[{},{},{}]'.format(
                self.type, 
                self.__mantissa(),
                self.name, 
                self.content[:10] + '..',
                self.attrs,
            )
        else:
            return '{}{}'.format(self.type, self.__mantissa())

    def __repr__(self):
        return str(self)


class DOMTree(object):
    def __init__(self, html):
        self._soup = BeautifulSoup(html, 'html.parser')
        self._steps_applied = []
        self._nodes_applied = []
        self._cache = {}
        self._cache_validities = {}

    def step_forward(self, step):
        if not self._find_all() and step.type != Step.A:
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
        self._invalidate_cache('_find_all')
        return self

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
        if current.find_all(string=False):
            current.unwrap()
        # otherwise decompose the node.
        else:
            current.decompose()
        return previous

    def _modify(self, step):
        # TODO: MODIFY SHOULD ONLY CHANGE ATTRIBUTES, NAME or STRING CONTENT 
        #       OF A NODE
        tag = self._new_tag(step)
        current = self._get_tag(step.target)
        previous = copy.deepcopy(current)
        current.replace_with(tag)
        return previous

    def _new_tag(self, step):
        if step.type not in (Step.W, Step.A, Step.M):
            raise TypeError('We can only make new tag for A and M step')

        # create new tag for the tree from the given step.
        if step.name:
            tag = self._soup.new_tag(step.name, **step.attrs)
            if step.content:
                tag.append(step.content)
        else:
            tag = step.content
        return tag

    def _get_tag(self, percentile):
        index = int((len(self) - 1) * percentile)
        return self._find_all()[index]

    def _find_all(self, *args, **kwargs):
        cache = self._get_cache('_find_all')
        if cache:
            return cache
        else:
            if kwargs.get('string') is None:
                kwargs['string'] = False
            nodes = self._soup.find_all(*args, **kwargs)
            self._set_cache('_find_all', nodes)
            return nodes

    def _all_tag_names(self):
        return {t.name for t in self._find_all()}

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
        return len(self._find_all())
