import inspect
from troposphere import (
    Ref, Output,
    Template, Parameter, BaseAWSObject
)


def get_class_attrs(cls):
    attributes = inspect.getmembers(
        cls, lambda a: not(inspect.isroutine(a))
    )
    return [
        attr[0]
        for attr in attributes
        if not attr[0].startswith('_')
    ]


class BaseTemplate(object):

    def __init__(self):
        self._template = Template()

    def add_description(self):
        self._template.add_description(
            self.description
        )

    def add_parameters(self):
        for key, values in self.parameters.items():
            self._template.add_parameter(
                Parameter(key, **values)
            )

    def add_conditions(self):
        for key, condition in self.conditions.items():
            self._template.add_condition(
                key, condition
            )

    def add_mappings(self):
        for key, mapping in self.mappings.items():
            self._template.add_mapping(
                key, self.mappings[key]
            )

    def add_outputs(self):
        for output_id, ref in self.output.items():
            self._template.add_output(
                Output(output_id, Value=Ref(ref))
            )

    def add_resource(self, attr_name):
        attr = getattr(self, attr_name)
        if isinstance(attr, list):
            if self.verify_list_of_resources(attr):
                for item in attr:
                    self._template.add_resource(item)
        elif isinstance(attr, BaseAWSObject):
            self._template.add_resource(attr)

    def verify_list_of_resources(self, attr):
        for item in attr:
            if not isinstance(item, BaseAWSObject):
                return False
        return True

    def render(self, mappings):
        self.mappings = mappings
        self.add_mappings()

        valid_attributes = get_class_attrs(self.__class__)
        for attr in valid_attributes:
            add_method = getattr(
                self, 'add_%s' % attr, None
            )
            if add_method:
                add_method()
            else:
                self.add_resource(attr)

        return self._template.to_json()
