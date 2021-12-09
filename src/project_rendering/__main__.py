from rendering import get_product_parser, render_project

if __name__ == '__main__':
    product_parser = get_product_parser()
    parsed_args, _ = product_parser.parse_known_args()

    try:
        # convert to a dictionary and resubmit
        render_project(vars(parsed_args))
    except KeyError:
        product_parser.print_usage()
