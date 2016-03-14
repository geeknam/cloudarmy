import boto3
import os
import sys
import yaml
from urlparse import urlparse

from cloudarmy.core import registry


class CloudArmy(object):

    def __init__(self, template_dir, environment_type, **kwargs):
        self.cf = boto3.client('cloudformation')
        self.s3 = boto3.resource('s3')

        # TODO: env var
        self.template_dir = template_dir
        sys.path.insert(0, self.template_dir)

        self.environment_type = environment_type
        self.settings = self.load_settings()
        self.output_dir = self.settings['OutputDir']
        self.mappings = self.load_mappings()
        self.templates = self.load_templates()

    def load_yaml(self, yaml_file):
        print('Loading %s...' % yaml_file)
        yaml_mappings = open(
            os.path.join(self.template_dir, yaml_file), 'rb'
        ).read()
        return yaml.load(yaml_mappings)

    def load_mappings(self):
        try:
            return self.load_yaml('mappings.yml')
        except IOError:
            print('No mappings.yml file found')
            return

    def load_settings(self):
        return self.load_yaml('settings.yml')

    def load_templates(self):
        for file in os.listdir(self.template_dir):
            file_name, ext = file.split('.')
            # Looks like a template, import it
            if ext == 'py':
                __import__(file_name)
        return registry.templates

    @property
    def s3_root_dir(self):
        return self.settings[
            self.environment_type
        ]['TemplateURL'].rsplit('/', 1)[0]

    @property
    def s3_directory(self):
        return urlparse(self.s3_root_dir).path[1:]

    @property
    def s3_bucket_name(self):
        return urlparse(
            self.settings[self.environment_type]['TemplateURL']
        ).netloc.split('.', 1)[0]

    @property
    def parameters(self):
        return self.settings['parameters']

    def render(self):
        for template in self.templates:
            template_class = template['template']
            rendered_template = template_class().render(
                self.mappings
            )
            output_file = os.path.join(
                self.output_dir, '%s.json' % template['template_name']
            )
            template_file = open(output_file, 'wb')
            template_file.write(rendered_template)
            template_file.close()
            print('Saved template to: %s' % output_file)

    def upload_templates_to_s3(self):
        for template in self.templates:
            output_file = os.path.join(
                self.output_dir, '%s.json' % template['template_name']
            )
            s3_path = '{s3_directory}/{template_name}.json'.format(
                s3_directory=self.s3_directory,
                template_name=template['template_name']
            )
            print('Uploading to S3: %s ...' % s3_path)
            self.s3.meta.client.upload_file(
                output_file, self.s3_bucket_name, s3_path
            )

    def create_stack(self):
        self.render()
        stack_settings = self.settings[self.environment_type]

        # If no template url, use template cbody refered by the name
        if 'TemplateURL' not in stack_settings:
            output_dir = self.settings['OutputDir']
            output_file = os.path.join(
                output_dir, '%s.json' % stack_settings.pop('TemplateName')
            )
            template_content = open(output_file, 'rb').read()
            stack_settings['TemplateBody'] = template_content
        else:
            self.upload_templates_to_s3()

        print('Creating stack: %s' % stack_settings['StackName'])
        response = self.cf.create_stack(
            **stack_settings
        )
        return response
