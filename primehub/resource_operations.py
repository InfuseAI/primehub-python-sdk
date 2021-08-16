from primehub.utils import resource_not_found


class GroupResourceOperation(object):

    def do_list(self, query, resource_key):
        current_group = self.group_name

        results = self.request({}, query)
        for g in results['data']['me']['effectiveGroups']:
            if current_group == g['name']:
                return g[resource_key]
        return []

    def do_get(self, query, resource_key, resource_name):
        resources = self.do_list(query, resource_key)
        data = [x for x in resources if x['name'] == resource_name]
        if data:
            return data[0]
        resource_not_found(resource_key, resource_name, 'name')
