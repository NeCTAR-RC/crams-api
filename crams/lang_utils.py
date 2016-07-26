# coding=utf-8
"""
    Python utils
"""


def strip_lower(str):
    return str.strip().lower()


def generate_project_role(project_name, role_name):
    return strip_lower(project_name) + '_' + strip_lower(role_name)


# http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/
def reverse_dict(d):
    return {v: k for k, v in d.items()}


def update_return_dict(map, key, value):
    map.update({key: value})
    return map


class Bunch(list):

    """

    :param args:
    :param kw:
    """

    def __init__(self, *args, **kw):
        super().__init__()
        self[:] = list(args)
        setattr(self, '__dict__', kw)


class BunchDict(dict):

    """

    :param kw:
    """

    def __init__(self, **kw):
        # noinspection PyTypeChecker
        dict.__init__(self, kw)
        self.__dict__ = self

    def __str__(self):
        state = ["%s=%r" % (attribute, value)
                 for (attribute, value)
                 in self.__dict__.items()]
        return '\n'.join(state)


# http://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
class CommonEqualityMixin(object):
    """
        Common Equality Mixin
    """
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class SortableObject(CommonEqualityMixin):
    """

    :param obj:
    :param sort_lambda:
    """

    def __init__(self, obj, sort_lambda):
        self.obj = obj
        self.sortLambda = sort_lambda

    def is_same_internal_object(self, other):
        """

        :param other:
        :return:
        """
        if (isinstance(other, type(self))) or\
                (isinstance(self.obj, type(other))):
            return other.obj == self.obj
        return False
