cloudarmy
=================
.. image:: https://travis-ci.org/geeknam/cloudarmy.svg?branch=master
    :target: https://travis-ci.org/geeknam/cloudarmy

A better workflow for developing and deploying `AWS Cloudformation <https://aws.amazon.com/cloudformation/>`_ templates. Compose Cloudformation templates with Python classes and manage configurations with yaml files.


**cloudarmy** consists of:

- A command-line tool for rendering, and deploying AWS Clouformation templates
- Easy development workflow for developing complex Cloudformation stacks (with `.yml` configuration files)
- Extendable / reusable Python classes for composing Cloudformation templates with the use of `troposphere <https://github.com/cloudtools/troposphere>`_


Installation
------------


.. code-block:: bash

    $ pip install cloudarmy


Getting Started
----------------

**Create a project directory**

.. code-block:: bash

    $ mkdir mystack

**Project structure**

.. code-block:: bash


    mystack
    ├── __init__.py
    ├── ec2_instance.py
    ├── mappings.yml
    └── settings.yml

**Render templates**

.. code-block:: bash

    $ cloudarmy render /path/to/mystack/ staging

*/path/to/mystack/* is your project directory.
*staging* is the environment you have defined in `settings.yml`.

cloudarmy is opinionated and requires you to define different environments in your settings

**Settings file**

.. code-block:: yaml

    # This is where the .json templates will be saved
    OutputDir: /tmp/cloudarmy_tests/

    staging:
      StackName: cloudarmy_ec2_test
      TemplateURL: https://mys3bucket.s3.amazonaws.com/templates/ec2.json
      DisableRollback: false
      TimeoutInMinutes: 10
      Capabilities:
        - CAPABILITY_IAM
      Parameters:
        -
          ParameterKey: EnvironmentType
          ParameterValue: staging
          UsePreviousValue: false
        -
          ParameterKey: KeyName
          ParameterValue: staging-key-pair
          UsePreviousValue: false

**Template class**

.. code-block:: python

    from cloudarmy.core.base import BaseTemplate
    from cloudarmy.contrib.mixins.environment import EnvironmentMixin
    from cloudarmy.core import register
    from troposphere.ec2 import Instance
    from troposphere import Base64, FindInMap, GetAtt
    from troposphere import Ref


    @register('ec2')
    class EC2Template(BaseTemplate, EnvironmentMixin):

        instance = Instance(
            'Ec2Instance',
            ImageId=FindInMap('RegionMap', Ref('AWS::Region'), 'AMI'),
            InstanceType=FindInMap(
                'EnvironmentType', Ref('EnvironmentType'), 'InstanceType'
            ),
            KeyName=Ref('KeyName'),
            SecurityGroups=['default'],
            UserData=Base64('80')
        )

        outputs = {
            'InstanceId': {
                'Description': 'InstanceId of the newly created EC2 instance',
                'Value': Ref('Ec2Instance'),
            },
            'AZ': {
                'Description': 'Availability Zone of the created EC2 instance',
                'Value': GetAtt('Ec2Instance', 'AvailabilityZone'),
            },
            "PublicIP": {
                'Description': 'Public IP address of the created EC2 instance',
                'Value': GetAtt('Ec2Instance', 'PublicIp'),
                'Condition': 'IsStaging'
            }
        }

        @property
        def parameters(self):
            parameters = EnvironmentMixin.parameters
            parameters.update({
                'KeyName': {
                    'Type': 'String',
                    'Description': 'Name of an existing EC2 KeyPair to enable SSH'
                }
            })
            return parameters





Documentation
---------------

Checkout the `examples <https://github.com/geeknam/cloudarmy/tree/master/examples>`_
