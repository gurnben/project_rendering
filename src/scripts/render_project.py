import project_rendering

if __name__ == '__main__':
    product_parser = project_rendering.get_product_parser()
    parsed_args, _ = product_parser.parse_known_args()

    try:
        # convert to a dictionary and resubmit
        project_rendering.render_project(vars(parsed_args))
    except KeyError:
        product_parser.print_usage()
