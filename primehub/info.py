from collections import OrderedDict

from primehub import Helpful, cmd, Module


class CliInformation(Helpful, Module):

    # TODO we should support group-context aware
    # TODO create a decorator @group_required
    @cmd(name='info', description='Show PrimeHub Cli information')
    def info(self):
        output = OrderedDict()
        me = self.primehub.me.me()
        output['me'] = me

        current_group = self.primehub.group.get(self.primehub.primehub_config.group)
        output['currentGroup'] = current_group
        return output

    def help_description(self):
        return "Display the user information and the selected group information"
