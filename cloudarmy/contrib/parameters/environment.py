

class EnvironmentParameter(object):

    parameters = {
        'EnvironmentType': {
            'Type': 'String',
            'Description': 'Production or Staging?'
        },
        'EnvironmentName': {
            'Type': 'String',
            'Description': 'Give this a name'
        }
    }
