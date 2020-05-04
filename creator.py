import create_options
import os
import shutil
import staff

def delete_and_create_folder(f):
    if os.path.isdir(f):
        shutil.rmtree(f)
    os.makedirs(f) # works recursively

def main():
    options = create_options.get_options()
    delete_and_create_folder(options["output_folder_complete"])
    staffs = staff.get_staffs(options["lily_file"])




if __name__ == '__main__':
    main()
