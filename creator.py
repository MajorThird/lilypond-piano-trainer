import create_options


def delete_and_create_folder(f):
    if os.path.isdir(f):
        shutil.rmtree(f)
    os.mkdir(f)

def main():
    options = create_options.get_options()
    delete_and_create_folder(options["output_folder_complete"])

if __name__ == '__main__':
    main()
