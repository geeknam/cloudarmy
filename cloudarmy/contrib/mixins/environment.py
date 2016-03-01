from cloudarmy.contrib.parameters.environment import EnvironmentParameter
from cloudarmy.contrib.conditions.environment import EnvironmentCondition


class EnvironmentMixin(EnvironmentParameter, EnvironmentCondition):
    pass
