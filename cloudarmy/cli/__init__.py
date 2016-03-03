import boto3
import os
import sys
import yaml
from urlparse import urlparse, urljoin

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
        print 'Loading %s...' % yaml_file
        yaml_mappings = open(
            os.path.join(self.template_dir, yaml_file), 'rb'
        ).read()
        return yaml.load(yaml_mappings)

    def load_mappings(self):
        return self.load_yaml('mappings.yml')

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
            print 'Saved template to: %s' % output_file

    def upload_templates_to_s3(self):
        for template in self.templates:
            output_file = os.path.join(
                self.output_dir, '%s.json' % template['template_name']
            )
            s3_path = '{s3_directory}/{template_name}.json'.format(
                s3_directory=self.s3_directory,
                template_name=template['template_name']
            )
            print 'Uploading to S3: %s ...' % s3_path
            self.s3.meta.client.upload_file(
                output_file, self.s3_bucket_name, s3_path
            )

    def create_stack(self):
        self.render()
        self.upload_templates_to_s3()
        response = self.cf.create_stack(
            **self.settings[self.environment_type]
        )
        return response
