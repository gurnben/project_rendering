import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import project_rendering

if __name__ == '__main__':
    product_parser = project_rendering.get_product_parser()
    parsed_args, _ = product_parser.parse_known_args()
    project_rendering.render_project(vars(parsed_args))

    try:
        # convert to a dictionary and resubmit
        project_rendering.render_project(vars(parsed_args))
    except KeyError:
        product_parser.print_usage()
