import click
from cloudarmy.cli import CloudArmy
import pprint
import webbrowser


@click.group()
def main():
    pass


@main.command()
@click.argument('template_dir')
@click.argument('environment_type')
def render(**kwargs):
    ca = CloudArmy(**kwargs)
    ca.render()


@main.command()
@click.argument('template_dir')
@click.argument('environment_type')
def upload_s3(**kwargs):
    ca = CloudArmy(**kwargs)
    ca.upload_templates_to_s3()


@main.command()
@click.argument('template_dir')
@click.argument('environment_type')
def validate(**kwargs):
    ca = CloudArmy(**kwargs)
    pprint.pprint(
        ca.cf.validate_template(
            TemplateURL=ca.settings[ca.environment_type]['TemplateURL']
        )
    )


@main.command()
@click.argument('template_dir')
@click.argument('environment_type')
def cost(**kwargs):
    ca = CloudArmy(**kwargs)
    url = ca.cf.estimate_template_cost(
        TemplateURL=ca.settings[ca.environment_type]['TemplateURL'],
        Parameters=ca.settings[ca.environment_type]['Parameters']
    )['Url']
    webbrowser.open(url)


@main.command()
@click.argument('template_dir')
@click.argument('environment_type')
def create_stack(**kwargs):
    ca = CloudArmy(**kwargs)
    ca.create_stack()


@main.command()
@click.argument('template_dir')
@click.argument('environment_type')
def delete_stack(**kwargs):
    ca = CloudArmy(**kwargs)
    ca.cf.delete_stack(
        StackName=ca.settings[ca.environment_type]['StackName']
    )


if __name__ == '__main__':
    main()
