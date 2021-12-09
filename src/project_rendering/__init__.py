import argparse
from pathlib import Path
# import sys
from jinja2 import Template
import yaml


def get_product_parser():
    """
    Get the argument parser for generating the CPaaS product.yml file.
    """

    # Generate a base parser
    description = "Parse configuration files to generate a CPaaS product.yml file"
    epilog = ""
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("--version", action="version", version="%(prog)s 0.0.1")
    parser.add_argument(dest="product_config",
                        help="product configuration input yaml file",
                        metavar="PRODUCT_CONFIGURATION_YAML_PATH",
                        type=lambda p: Path(p).absolute())
    parser.add_argument(dest="builds_config",
                        help="builds configuration input yaml file",
                        metavar="BUILDS_CONFIGURATION_YAML_PATH",
                        type=lambda p: Path(p).absolute())
    parser.add_argument("-t",
                        dest="jinja_template",
                        help="product jinja template override",
                        metavar="PRODUCT_JINJA_TEMPLATE_PATH",
                        type=lambda p: Path(p).absolute(),
                        default=Path(__file__).absolute().parent / "templates/product.yaml.jinja",
                        required=False)
    parser.add_argument("-o",
                        dest="product_output",
                        help="output file location for product.yaml",
                        metavar="PRODUCT_YAML_OUTPUT_PATH",
                        type=lambda p: Path(p).absolute(),
                        default="product.yml",
                        required=False)
    return parser


def render_project(arg_dict):
    """
    Load configuration files, convert nudges to depends-on, and render the product.yaml

    :param arg_dict: Dictionary containing arguments for rendering the project. Required keys are
                     `product_config`, `builds_config`, `jinja_template`, and `product_output`.
    """
    with open(arg_dict["product_config"], "r") as stream:
        product_config = yaml.safe_load(stream)

    with open(arg_dict["builds_config"], "r") as stream:
        builds = yaml.safe_load(stream)

    with open(arg_dict["jinja_template"], "r") as stream:
        template_content = stream.read()

    template = Template(template_content, extensions=['jinja2.ext.do'])

    # To allow lazier filling of the builds, we allow for default midstream/builds to be injected
    inject_midstream = product_config.setdefault('inject-default-midstream', False)
    inject_builds = product_config.setdefault('inject-default-builds', False)
    if inject_midstream or inject_builds:
        # print(builds)
        for project in builds:
            builds[project] = {} if builds[project] is None else builds[project]
            # print(project)
            # print(builds[project])
            if inject_midstream:
                builds[project].setdefault('midstream', {'project': project})
                # if builds[project].setdefault('midstream', []) is not None:
                #     builds[project]['midstream'].setdefault('project', project)
            if inject_builds:
                builds[project].setdefault('builds', [{'name': project}])

    if product_config.get('use-depends-on', False):
        # Let's parse the builds to create the depends-on relationships instead of using priorities
        # By basing all build names looking for the `nudges` key

        # All names should be unique in order for this to work
        build_names = set()
        duplicate_names = set()
        nudge_map = {}
        default_nudges = set(product_config.get('default-nudge', []))

        # print(builds)
        for project in builds:
            project_default_nudge = default_nudges
            if builds[project].get('nudges', []):
                project_default_nudge = builds[project]['nudges']
            # print('project: {}'.format(project))
            for component in builds[project]['builds']:
                # print('component: {}'.format(component))
                component_name = component.get('name')
                # print('component_name: {}'.format(component_name))
                if component_name not in build_names:
                    build_names.add(component_name)
                else:
                    duplicate_names.add(component_name)
                component_nudges = project_default_nudge
                if component.get('nudges', []):
                    component_nudges = component['nudges']
                if component_nudges:
                    for nudge in set(component_nudges):
                        nudge_map.setdefault(nudge, []).append(component_name)

        if len(duplicate_names) != 0:
            raise(Exception('Depends-on cannot be used; duplicate names detected: {}'.format(duplicate_names)))

    # print(builds)
        for project in builds:
            # print('project: {}'.format(project))
            for component in builds[project]['builds']:
                # print('component: {}'.format(component))
                component_name = component.get('name')
                dependent_components = nudge_map.get(component_name, None)
                if dependent_components is not None:
                    component['depends-on'] = dependent_components

    with open(arg_dict["product_output"], "w") as stream:
        stream.write(template.render(builds=builds, product_config=product_config))
