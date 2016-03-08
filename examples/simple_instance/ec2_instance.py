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
