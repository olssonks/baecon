import baecon as bc

def main():
    args = bc.utils.arg_parser()
    bc.utils.generate_measurement_config_from_file(args.gen_config,
                                                   args.output_file)
    return
    
if __name__ == '__main__':
    main()