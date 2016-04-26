# coding=utf-8
"""
    Python utils
"""
__author__ = 'Rafi M Feroze'

# http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/


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
