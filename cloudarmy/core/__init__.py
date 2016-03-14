
class TemplateRegistry(object):

    def __init__(self):
        self.templates = []

    def register(self, template_name, template_class):
        self.templates.append({
            'template': template_class,
            'template_name': template_name
        })

    def clear(self):
        self.templates = []


registry = TemplateRegistry()


def register(template_name):
    def wrapped(template_class):
        registry.register(template_name, template_class)
    return wrapped
