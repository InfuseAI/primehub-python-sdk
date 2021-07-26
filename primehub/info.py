from primehub import Helpful, cmd, Module


class CliInformation(Helpful, Module):

    @cmd(name='info', description='Show PrimeHub Cli information')
    def info(self):
        me = self.primehub.me.me()
        me['user_id'] = me['id']

        current_group = self.primehub.group.get(self.primehub.primehub_config['group'])
        images = [x['name'] for x in current_group['images']]
        instance_types = [x['name'] for x in current_group['instanceTypes']]
        datasets = [x['name'] for x in current_group['datasets']]

        if not current_group:
            group_status = " (No matched group for name %s)" % self.primehub.primehub_config['group']
        else:
            group_status = """
  Id: %(id)s
  Name: %(name)s
  Display Name: %(displayName)s
  Group Quota:
    CPU: %(projectQuotaCpu)s
    GPU: %(projectQuotaGpu)s
    Memory: %(projectQuotaMemory)s
  User Quota:
    CPU: %(quotaCpu)s
    GPU: %(quotaGpu)s
    Memory: %(quotaMemory)s
            """ % current_group

        def indent2(lines):
            return "\n  ".join(lines)

        args = dict(endpoint=self.primehub.primehub_config['endpoint'], group_status=group_status.strip(),
                    images=indent2(images), instance_types=indent2(instance_types), datasets=indent2(datasets))
        output = """Endpoint: %(endpoint)s
User:
  Id: %(user_id)s 
  Username: %(username)s
  Email: %(email)s
  First Name: %(firstName)s
  Last Name: %(lastName)s
  Is Admin: %(isAdmin)s
Current Group:
  %(group_status)s
Images:
  %(images)s
InstanceTypes:
  %(instance_types)s
Datasets:
  %(datasets)s
""" % ({**me, **args})
        return output

    def help_description(self):
        return "Display the user information and the selected group information"
