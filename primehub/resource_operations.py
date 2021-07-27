from primehub.utils import group_required


class GroupResourceOperation(object):

    def do_list(self, query, resource_key):
        if not self.primehub_config.group_info:
            group_required()

        results = self.request({}, query)
        for g in results['data']['me']['effectiveGroups']:
            if self.primehub_config.group_info['name'] == g['name']:
                return g[resource_key]
        return []

    def do_get(self, query, resource_key, resource_name):
        resources = self.do_list(query, resource_key)
        data = [x for x in resources if x['name'] == resource_name]
        if data:
            return data[0]
        return None
