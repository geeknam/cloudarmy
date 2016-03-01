from troposphere import Ref, Equals


class EnvironmentCondition(object):

    conditions = {
        "IsProduction": Equals(
            Ref("EnvironmentType"), "production"
        ),
        "IsStaging": Equals(
            Ref("EnvironmentType"), "staging"
        ),
    }
