from file_handling import *

def main():
    config = ConfigManager('config.txt')
    geo_dir = config.get_geo_dir()
    taf_dir = config.get_taf_dir()
    file_manager = FileManager(taf_dir, geo_dir)
    part_number = input('Enter the part number to search for: ')
    new_revision = input("Please enter the new revision: ")
    file_manager.read_and_update_taf_files(part_number, new_revision, None, "TAF_Temp")
    
if __name__ == "__main__":
    main()