from file_handling import *

def main():
    config = ConfigManager('config.txt') # Create a config from the config.txt in the current working directory
    geo_dir = config.get_geo_dir() # Get the directory for the GEO files from the config
    taf_dir = config.get_taf_dir() # Get the directory for the TAF files from the config
    backup_dir = config.get_backup_dir() # Get the directory for the backup files from the config
    file_manager = FileManager(taf_dir, geo_dir, backup_dir) # Create the file manager at the configured directories
    
    # Run the main loop of the program until the user requests to end it
    mainLoop = True
    while mainLoop == True:
        part_number = input('Enter the part number to search for: ')
        new_revision = input('Please enter the new revision: ')
        specific_file = input('Would you like to update the whole directory? (Y/N): ')
        
        # Checks if the user wants to update the whole directory or just one TAF file
        if specific_file == 'Y':
            status = file_manager.read_and_update_taf_files(part_number, new_revision, None, "TAF_Temp")
            
            # If the status variable was returned as True then the GEO doesn't exist. 
            # The user is prompted to confirm they want to proceed with the modifications.
            if status:
                # Run the update function again overiding the existance check if the user wants to continue
                if input('The GEO does not exist, are you sure you wan\'t to update? (Y/N): ') == 'Y':
                    file_manager.read_and_update_taf_files(part_number, new_revision, None, "TAF_Temp", True)
                else:
                    print("Finished without modifications.")
                    
        # This runs if the user specified they only want to update specific TAF files
        else:
            cont = True
            
            # Run loop updating specific files until the user wants the end
            while cont:
                taf_file = input('Enter the name of the TAF file:')
                if not taf_file.lower().endswith('.taf'):
                    taf_file += '.TAF'
                file_manager.read_and_update_taf_files(part_number, new_revision, [taf_file], "TAF_Temp")
                if input('Would you like to update more TAFs? (Y/N): ').strip().upper() == 'N':
                    cont = False
        # Check if there are other files the user wants to update
        if input('Would you like to change another GEO? (Y/N): ') == 'N':
            mainLoop = False

# Check the script is being run as the main file
if __name__ == "__main__":
    main()