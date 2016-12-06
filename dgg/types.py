import copy
from bs4 import BeautifulSoup, NavigableString, Tag


class Step(object):
    A = APPEND = 'A'
    M = MODIFY = 'M'
    D = DELETE = 'D'
    TYPES = (A, M, D)

    @classmethod
    def generate(cls, tree_from, tree_to, type):
        # TODO: SHOULD GENERATE a step which has a appropriate target index
        #       that's compatible with current tree. Combination of name, 
        #       content and attributes also should be choosen carefully
        #       within tree_to's conditions.
        pass

    def __init__(self, type, target, name=None, content=None, attributes=None):
        if type not in Step.TYPES:
            raise TypeError('Invalid step type: {}'.format(type))

        if type == Step.A and (not name and not content):
            raise ValueError(''.join([
                'Append step should contain at least one of tag ',
                'name or content'
            ]))

        if type == Step.M and (not name and not content and not attributes):
            raise ValueError(''.join([
                'Modify step should contain at least one of tag name, content ',
                'or attributes'
            ]))

        self.type = type
        self.target = target
        self.name = name
        self.content = content
        self.attributes = attributes

    def __eq__(self, other):
        if self.type != other.type:
            return False

        if self.type in (Step.A, Step.M):
            return self.name == other.name and \
                self.content == other.content and \
                self.attributes == other.attributes
        else:
            return True

    def __str__(self):
        if self.type in (Step.A, Step.M):
            return '{}{}[{},{},{}]'.format(
                self.type, 
                self.target,
                self.name, 
                self.content[:10] + '..',
                self.attributes
            )
        else:
            return '{}{}'.format(self.type, self.target)

    def __repr__(self):
        return str(self)


class DOMTree(object):
    def __init__(self, html):
        self._soup = BeautifulSoup(html, 'html.parser')
        self._steps_applied = []
        self._nodes_applied = []
        self._cache = {}

    def step_forward(self, step):
        if not self._find_all() and step.type != Step.A:
            return

        if step.type == Step.A:
            node_applied = self._append(step)
        elif step.type == Step.M:
            node_applied = self._modify(step)
        else:
            node_applied = self._delete(step)

        # record the step and applied node
        self._steps_applied.append(step)
        self._nodes_applied.append(node_applied)
        return self

    @property
    def steps_applied(self):
        return self._steps_applied

    @property
    def nodes_applied(self):
        return self._nodes_applied

    def _append(self, step):
        tag = self._new_tag(step)
        current = self._get_tag(step.target)
        previous = copy.deepcopy(current)
        current.append(tag)
        return previous

    def _modify(self, step):
        # TODO: MODIFY SHOULD ONLY CHANGE ATTRIBUTES, NAME or STRING CONTENT 
        #       OF A NODE
        tag = self._new_tag(step)
        current = self._get_tag(step.target)
        previous = copy.deepcopy(current)
        current.replace_with(tag)
        return previous

    def _delete(self, step):
        # TODO: MODIFY SHOULD ONLY DELETE A LEAF NODE
        current = self._get_tag(step.target)
        previous = copy.deepcopy(current)
        current.decompose()
        return previous

    def _get_tag(self, index):
        return self._find_all()[index]

    def _new_tag(self, step):
        if step.type not in (Step.A, Step.M):
            raise TypeError('We can only make new tag for A and M step')

        # create new tag for the tree from the given step.
        if step.name:
            tag = self._soup.new_tag(step.name, **step.attributes)
            if step.content:
                tag.append(step.content)
        else:
            tag = step.content
        return tag

    def _find_all(self, *args, **kwargs):
        if self._invalid or not self._cache.get('_find_all'):
            if kwargs.get('string') is None:
                kwargs['string'] = False
            self._cache['_find_all'] = self._soup.find_all(*args, **kwargs)
        return self._cache['_find_all']

    def _all_tag_names(self):
        return {t.name for t in self._find_all()}

    def _all_attributes(self):
        # TODO: NOT IMPLEMENTED YET
        pass

    def _all_contents(self):
        # TODO: NOT IMPLEMENTED YET
        pass

    def __str__(self):
        return self._soup.prettify()

    def __repr__(self):
        return str(self)
