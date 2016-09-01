from django import template

register = template.Library()


@register.filter(name='filter_project_id')
def get_project_id(project_ids, system_to_search):
    search_tree_hierarchy = ['system', 'system']
    for project_id in project_ids:
        try:
            if DictSearch.search_tree_return_value(
                    search_tree_hierarchy, project_id) == system_to_search:
                return project_id['identifier']
        except Exception:
            pass

    return None


@register.filter(name='filter_project_contact')
def get_project_contact_email(project_contacts, role_name):
    search_tree_hierarchy = ['contact_role', 'name']
    for project_contact in project_contacts:
        try:
            if DictSearch.search_tree_return_value(
                    search_tree_hierarchy, project_contact) == role_name:
                return project_contact['contact']['email']

        except Exception:
            pass

    return None


@register.filter(name='filter_question_response')
def get_response_for_question(question_responses, question_key):
    search_tree_hierarchy = ['question', 'key']
    for question_response in question_responses:
        try:
            if DictSearch.search_tree_return_value(
                    search_tree_hierarchy, question_response) == question_key:
                return question_response['question_response']

        except Exception:
            pass

    return None


class DictSearch:
    ALL = '*'

    @classmethod
    def search_tree_return_value(cls, search_hierarchy, search_dict):
        """
        Search a multi-level Dictionary for a hierarchy of keys and return the
        value if found.
        Use wildcard '*' at any level for a blind search. The first match will
        be returned for such blind search.

        For example if the dict was
        {
            'question_response': '',
            'question': {
                   'key': 'usagepattern',
                   'question': 'Instance, object storage and volume storage'
                   },
            'id': 10346
        }

        For search_hierarchy ['question', 'key'] and ['*', 'key'] the same
          value will be returned i.e., 'usagepattern'

        But the return value for ['question', '*'] or ['*','*'] is arbitrary.
        Such constructs are useful for determining the minimum tree depth of
        the dictionary

        :param search_hierarchy:
        :param search_dict:
        :return:
        """
        remaining_tree = list(search_hierarchy)
        while remaining_tree:
            if isinstance(search_dict, dict):
                next_node = remaining_tree.pop(0)
                if next_node == DictSearch.ALL:
                    for value_sub_dict in search_dict.values():
                        try:
                            return DictSearch.search_tree_return_value(
                                remaining_tree, value_sub_dict)
                        except Exception:
                            continue
                elif next_node in search_dict:
                    return DictSearch.search_tree_return_value(
                        remaining_tree,
                        search_dict.get(next_node))
                else:
                    raise Exception('Tree Not Found')
            else:
                raise Exception('Tree Not Found')

        return search_dict
