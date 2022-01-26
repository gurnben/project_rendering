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

    # Lump as many tasks together in this first iteration as possible
    #       but only iterate if needed
    # - injecting midstream
    # - injecting builds
    # - gathering dependencies

    # To allow lazier filling of the builds, we allow for default midstream/builds to be injected
    inject_midstream = product_config.setdefault('inject-default-midstream', False)
    inject_builds = product_config.setdefault('inject-default-builds', False)

    # allow specification of nudges on components for easier depends-on leveraging nudges
    use_depends_on = product_config.setdefault('use-depends-on', False)
    build_names = set()
    duplicate_names = set()
    nudge_map = {}
    project_map = {}
    default_nudges = set(product_config.get('default-nudge', []))

    # print(builds)
    if inject_builds or inject_builds or use_depends_on:
        for project_name, project in builds.items():
            # protect agains an undefined build in case we are using a default
            builds[project_name] = {} if project is None else project
            if inject_midstream:
                builds[project_name].setdefault('midstream', {'project': project_name})
            if inject_builds:
                builds[project_name].setdefault('builds', [{'name': project_name}])

            if use_depends_on:
                project_default_nudge = default_nudges
                if builds[project_name].get('nudges', []):
                    project_default_nudge = builds[project_name]['nudges']
                # print('project: {}'.format(project))
                component_index = 0
                for component in builds[project_name]['builds']:
                    # print('component: {}'.format(component))
                    component_name = component.get('name')
                    project_map[component_name] = (project_name, component_index)
                    # print('component_name: {}'.format(component_name))
                    if component_name not in build_names:
                        build_names.add(component_name)
                    else:
                        duplicate_names.add(component_name)
                    component_nudges = project_default_nudge
                    # Allow nudge bails if we don't want this to nudge anything
                    # and a default is set -- by providing a non-list
                    if type(component.setdefault('nudges', [])) is not list:
                        print(f'`nudges` is not a list for build named {component_name}; skipping nudge.')
                        continue
                    elif component['nudges']:
                        component_nudges = component['nudges']
                    if component_nudges:
                        for nudge in set(component_nudges):
                            nudge_map.setdefault(nudge, []).append(component_name)
                    component_index += 1

            if len(duplicate_names) != 0:
                raise(Exception('Depends-on cannot be used; duplicate names detected: {}'.format(duplicate_names)))

    # print(builds)
    # if we are using depends-on nudges, iterate again to set the dependencies
    if use_depends_on:
        for project in builds:
            # print('project: {}'.format(project))
            for component, dependencies in nudge_map.items():
                component_project, component_index = project_map[component]
                if builds[component_project]['builds'][component_index]['name'] != component:
                    raise(Exception('Mismatch between component name and index'))
                builds[component_project]['builds'][component_index]['depends-on'] = dependencies

    with open(arg_dict["product_output"], "w") as stream:
        stream.write(template.render(builds=builds, product_config=product_config))
