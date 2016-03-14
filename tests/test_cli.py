import os
import json
import shutil
import unittest
import yaml
from mock import patch
from cloudarmy.cli import CloudArmy
from cloudarmy.core import registry
from cloudarmy.core.base import BaseTemplate


class CommandLineTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_template_dir = '/tmp/cloudarmy_tests/'
        os.environ['AWS_ACCESS_KEY_ID'] = 'myid'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
        os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
        try:
            os.mkdir(self.tmp_template_dir)
        except OSError:
            pass

        self.example_project_dir = os.path.normpath(
            os.path.join(os.getcwd(), 'examples/simple_instance')
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_template_dir)

    def write_settings(self, path, data):
        settings_file = open(path, 'wb')
        yaml_content = yaml.dump(data)
        settings_file.write(yaml_content)
        settings_file.close()

    def test_load_settings_no_file(self):
        with self.assertRaises(IOError):
            CloudArmy(
                template_dir=self.tmp_template_dir,
                environment_type='test'
            )

    def test_load_settings(self):
        settings = {
            'OutputDir': '/path/to/output/'
        }
        self.write_settings(
            '%ssettings.yml' % self.tmp_template_dir,
            settings
        )
        ca = CloudArmy(
            template_dir=self.tmp_template_dir,
            environment_type='test'
        )
        self.assertEqual(ca.settings, settings)

    def test_load_templates(self):
        CloudArmy(
            template_dir=self.example_project_dir,
            environment_type='staging'
        )
        self.assertEqual(
            registry.templates[0]['template_name'], 'ec2'
        )
        self.assertTrue(
            issubclass(registry.templates[0]['template'], BaseTemplate)
        )

    def test_s3_root_dir(self):
        ca = CloudArmy(
            template_dir=self.example_project_dir,
            environment_type='staging'
        )
        self.assertEqual(
            ca.s3_root_dir,
            'https://mys3bucket.s3.amazonaws.com/templates'
        )

    def test_s3_directory(self):
        ca = CloudArmy(
            template_dir=self.example_project_dir,
            environment_type='staging'
        )
        self.assertEqual(
            ca.s3_directory,
            'templates'
        )

    def test_s3_bucket_name(self):
        ca = CloudArmy(
            template_dir=self.example_project_dir,
            environment_type='staging'
        )
        self.assertEqual(
            ca.s3_bucket_name, 'mys3bucket'
        )

    def test_render(self):
        ca = CloudArmy(
            template_dir=self.example_project_dir,
            environment_type='staging'
        )
        ca.render()
        self.assertTrue(os.path.exists(
            '%sec2.json' % ca.output_dir)
        )

    @patch('boto3.client')
    @patch('boto3.resource')
    def test_create_stack(self, mock_resource, mock_client):
        ca = CloudArmy(
            template_dir=self.example_project_dir,
            environment_type='staging'
        )
        ca.create_stack()
        self.assertTrue(
            mock_client.return_value.create_stack.called
        )

    @patch('boto3.client')
    @patch('boto3.resource')
    def test_create_stack_no_template_url(self, mock_resource, mock_client):
        ca = CloudArmy(
            template_dir=self.example_project_dir,
            environment_type='staging'
        )
        # Assume no TemplateURL and TemplateName is provided
        ca.settings['staging'].pop('TemplateURL')
        ca.settings['staging']['TemplateName'] = 'ec2'
        ca.create_stack()
        # Assert that TemplateBody is a valid json value
        template = json.loads(
            mock_client.return_value.create_stack.call_args[1][
                'TemplateBody'
            ]
        )
        self.assertIsInstance(template, dict)
