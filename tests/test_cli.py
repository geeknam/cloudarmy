import os
import shutil
import unittest
import yaml
from cloudarmy.cli import CloudArmy
from cloudarmy.core import registry
from cloudarmy.core.base import BaseTemplate


class CommandLineTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_template_dir = '/tmp/cloudarmy_tests/'
        os.environ['AWS_ACCESS_KEY_ID'] = 'myid'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
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
        self.assertEqual(registry.templates, [])

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

    def test_s3_directory(self):
        ca = CloudArmy(
            template_dir=self.example_project_dir,
            environment_type='staging'
        )
        self.assertEqual(
            ca.s3_root_dir,
            'https://mys3bucket.s3.amazonaws.com/templates'
        )

    def test_s3_bucket_name(self):
        ca = CloudArmy(
            template_dir=self.example_project_dir,
            environment_type='staging'
        )
        self.assertEqual(
            ca.s3_bucket_name, 'mys3bucket'
        )
