from file_handling import *

def main():
    config = ConfigManager('config.txt')
    geo_dir = config.get_geo_dir()
    taf_dir = config.get_taf_dir()
    backup_dir = config.get_backup_dir()
    file_manager = FileManager(taf_dir, geo_dir, backup_dir)
    mainLoop = True
    while mainLoop == True:
        part_number = input('Enter the part number to search for: ')
        new_revision = input('Please enter the new revision: ')
        specific_file = input('Would you like to update the whole directory? (Y/N): ')
        if specific_file == 'Y':
            status = file_manager.read_and_update_taf_files(part_number, new_revision, None, "TAF_Temp")
            if status:
                override = input('The GEO does not exist, are you sure you wan\'t to update? (Y/N)')
                if override == 'Y':
                    file_manager.read_and_update_taf_files(part_number, new_revision, None, "TAF_Temp", True)
                else:
                    print("Finished without modifications.")
        else:
            cont = True
            while cont:
                taf_file = input('Enter the name of the TAF file:')
                if not taf_file.lower().endswith('.taf'):
                    taf_file += '.TAF'
                file_manager.read_and_update_taf_files(part_number, new_revision, [taf_file], "TAF_Temp")
                if input('Would you like to update more TAFs? (Y/N)').strip().upper() == 'N':
                    cont = False
        if input('Would you like to change another GEO? (Y/N)') == 'N':
            mainLoop = False

if __name__ == "__main__":
    main()