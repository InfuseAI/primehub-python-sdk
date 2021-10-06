from typing import Iterator, Any

from primehub import Helpful, cmd, Module
from primehub.utils.display import display_tree_like_format


class AppTemplate(Helpful, Module):

    @cmd(name='list', description='List PhApp templates', return_required=True)
    def list(self) -> Iterator:
        """
        List PhApp templates

        :rtype: Iterator
        :returns: PhApp templates
        """
        query = """
        query GetPhAppTemplates {
          phAppTemplates {
            id
            name
            icon
            version
            description
            docLink
            template
          }
        }
        """
        result = self.request({}, query)
        if 'data' in result and 'phAppTemplates' in result['data']:
            result = result['data']['phAppTemplates']
            for template in result:
                yield template
        return result

    @cmd(name='get', description='Get a PhApp template', return_required=True)
    def get(self, id: str) -> dict:
        """
        Get a PhApp template

        :rtype: dict
        :returns: a PhApp template
        """
        query = """
        query GetPhAppTemplates($where: PhAppTemplateWhereInput) {
          phAppTemplates(where: $where) {
            id
            name
            icon
            version
            description
            docLink
            template
            defaultEnvs {
              name
              defaultValue
              optional
              description
            }
          }
        }
        """
        result = self.request({'where': {'id': id}}, query)
        if 'data' in result and 'phAppTemplates' in result['data']:
            result = result['data']['phAppTemplates']
            return result[0]
        return result

    def help_description(self):
        return "Get PhAppTemplates"

    def display(self, action: dict, value: Any):
        # customize the list view from columns to tree-like
        if action['func'] == AppTemplate.list.__name__ and self.get_display().name != 'json':
            for template in value:
                template = self.convert_for_human_friendly_data(template)
                display_tree_like_format(template, file=self.primehub.stdout)
                print("", file=self.primehub.stdout)
        elif action['func'] == AppTemplate.get.__name__ and self.get_display().name != 'json':
            super(AppTemplate, self).display(action, self.convert_for_human_friendly_data(value))
        else:
            super(AppTemplate, self).display(action, value)

    def convert_for_human_friendly_data(self, template):
        # drop template and icon for human-friendly view
        t = template.pop('template')
        template.pop('icon')
        if 'defaultEnvs' in template:
            template.pop('defaultEnvs')

        image = t.get('spec', {}).get('podTemplate', {}).get('spec', {}).get('containers', [{}])[0].get('image')
        template['image'] = image
        return template
