from cloudarmy.core import registry
import sys
import os
import yaml


class CloudArmy(object):

    def __init__(self, template_dir, output_dir, **kwargs):
        sys.path.insert(0, template_dir)
        # Where to look for python templates
        self.template_dir = template_dir
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = template_dir

        self.settings = self.load_settings()

    def load_settings(self):
        yaml_settings = open(
            os.path.join(self.template_dir, 'settings.yml'), 'rb'
        ).read()
        return yaml.load(yaml_settings)

    def load_templates(self):
        for file in os.listdir(self.template_dir):
            file_name, ext = file.split('.')
            # Looks like a template, import it
            if ext == 'py':
                __import__(file_name)

    def render(self):
        self.load_templates()
        for template in registry.templates:
            template_class = template['template']
            rendered_template = template_class().render(
                self.settings
            )
            output_file = os.path.join(
                self.output_dir, '%s.json' % template['template_name']
            )
            template_file = open(output_file, 'wb')
            template_file.write(rendered_template)
            template_file.close()


def main(args=None):
    template_dir = sys.argv[1]
    try:
        output_dir = sys.argv[2]
    except IndexError:
        output_dir = template_dir

    ca = CloudArmy(template_dir, output_dir)
    ca.render()

if __name__ == '__main__':
    main()
