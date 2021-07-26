from primehub import Helpful, cmd, Module


class Group(Helpful, Module):

    @cmd(name='list', description='List groups')
    def list(self):
        query = """
        {
          me {
            effectiveGroups {
              id
              name
              displayName
              # user quota
              quotaCpu
              quotaGpu
              quotaMemory
              # group quota
              projectQuotaCpu
              projectQuotaGpu
              projectQuotaMemory      
              images {
                id
                name
                displayName
                description        
                type
                url
                urlForGpu
                groupName
              }
              instanceTypes {
                id
                name        
                displayName
                description
              }
              datasets {
                id
                name
                displayName        
                description
              }
            }
          }
        }
        """
        results = self.request({}, query)
        return results['data']['me']['effectiveGroups']

    @cmd(name='get', description='Get group by name')
    def get(self, group_name):
        groups = self.list()
        group = [x for x in groups if x['name'] == group_name]
        if group:
            return group[0]
        return None

    def help_description(self):
        return "Get a group or list groups"
