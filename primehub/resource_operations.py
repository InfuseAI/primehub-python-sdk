from primehub import Helpful, cmd, Module, NoSuchGroup


class GroupResourceOperation(object):

    def do_list(self, query, resource_key):
        # self.primehub_config

        results = self.request({}, query)
        outputs = []
        for g in results['data']['me']['effectiveGroups']:
            if self.primehub_config.group == g['name']:
                outputs.extend(g[resource_key])
        return outputs

    def do_get(self, query, resource_key, resource_name):
        resources = self.do_list(query, resource_key)
        data = [x for x in resources if x['name'] == resource_name]
        if data:
            return data[0]
        return None
