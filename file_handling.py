import re
import os
import shutil
import datetime
class ConfigManager:
    def __init__(self, file_path):
        self.file_path = file_path
    def load_config(self):
        try:
            """Open the config file and return the contents"""
            with open(self.file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: The configuration file {self.file_path} was not found.")
            exit(1)
        except PermissionError:
            print(f"Error: Permission denied when trying to read {self.file_path}.")
            exit(1)
    def get_geo_dir(self):
        """Gets the GEO directory for the configuration"""
        config = self.load_config()
        matches = re.findall(r'GEO_DIR: "(.*)"', config)
        
        # Check if the line was found
        if not matches:
            raise ValueError("GEO_DIR configuration not found or is invalid in the configuration file.")
        print(f"GEO: {matches[0]}")
        return matches[0]   
    def get_taf_dir(self):
        """Gets the TAF directory from the configuration"""
        config = self.load_config()
        matches = re.findall(r'TAF_DIR: "(.*)"', config)
        
        # Check if the line was found
        if not matches:
            raise ValueError("TAF_DIR configuration not found or is invalid in the configuration file.")
        print(f"TAF: {matches[0]}")
        return matches[0]
    def get_backup_dir(self):
        """Gets the backup directory from the configuration"""
        config = self.load_config()
        matches = re.findall(r'BACKUP_DIR: "(.*)"', config)
        
        # Check if the line was found
        if not matches:
            raise ValueError("BACKUP_DIR configuration not found or is invalid in the configuration file.")
        return matches[0]
    
class FileManager:
    def __init__(self, taf_dir, geo_dir, backup_base_dir):
        self.taf_dir = taf_dir
        self.geo_dir = geo_dir
        self.backup_base_dir = backup_base_dir
        
        # Ensure the backup_base_dir exists
        if not os.path.exists(self.backup_base_dir):
            os.makedirs(self.backup_base_dir)
        
        # Creates a new backup directory 1 number higher than the last
        self.current_backup_dir = self.create_backup_dir()
        
        try:
            self.geo_list = [file for file in os.listdir(self.geo_dir) if file.endswith('.GEO')] # Get the list of GEO files (only needs to run once at init to save time)
        except FileNotFoundError:
            print(f"Error: The GEO directory {self.geo_dir} was not found.")
            exit(1)
        except PermissionError:
            print(f"Error: Cannot list contents of {self.geo_dir} due to lack of permissions.")
            exit(1)
    def search_for_tafs(self):
        """Search directory for .TAF files"""
        try:
            taf_list = [file for file in os.listdir(self.taf_dir) if file.lower().endswith('.taf')] # Get all TAF files
            return taf_list
        except FileNotFoundError:
            print("TAF directory not found")
            exit(1)
        except PermissionError:
            print("Can't search for .TAF files in this directory due to lack of permission")
            exit(1)
    def create_backup_dir(self):
        """Creates a new backup directory, incrementing the count for successive runs"""
        # Find the highest existing backup directory number and add one
        existing_backups = [d for d in os.listdir(self.backup_base_dir) if os.path.isdir(os.path.join(self.backup_base_dir, d))]
        if existing_backups:
            latest_backup = max([int(d.split('_')[-1]) for d in existing_backups if d.startswith('backup_') and d.split('_')[-1].isdigit()], default=0)
        else:
            latest_backup = 0
        new_backup_dir = os.path.join(self.backup_base_dir, f'backup_{latest_backup + 1}')
        os.makedirs(new_backup_dir, exist_ok=True)
        return new_backup_dir
    def copy_tafs_to_backup(self, file_path):
        """Copy the taf files to the backup folder before changing them"""
        shutil.copy(file_path, self.current_backup_dir) # Copies the files
    def search_for_geo(self, geo_name):
        """Searches for a geo file that matches the given name"""
        for name in self.geo_list: # Iterate through the list of GEO files to check if the part exists
            if name.lower() in geo_name.lower(): # Check if a part exists
                return True
        return False
    def read_and_update_taf_files(self, part_num, replace_version, taf_files = None, save_dir = None, override = False):
        """Reads each .TAF file, updates lines matching a pattern, and writes changes back."""
        if self.search_for_geo(part_num + '_' + replace_version + '.GEO') or override:
            part_num_escaped = re.escape(part_num)  # Convert any special characters to characters that are safe to use in regex pattern
            geo_pattern = rf"{part_num_escaped}_.*\.GEO"  # Pattern to match the GEO file name
            
            # Check if a taf file was given during function call
            if taf_files is None:
                taf_files = self.search_for_tafs()
                
            # Check if an alternate save directory was passed during function call (can be used for debugging)
            if save_dir is None:
                save_dir = self.taf_dir

            version_pattern = r"_(.*?)\."
            # Iterate through all the files in the taf_files list
            for taf_file in taf_files:
                found_indicator = False  # Indicator for whether the TAF was changed
                file_path = os.path.join(self.taf_dir, taf_file) # Combine the file with the file path in a system safe way
                temp_write_path = file_path + '.tmp'  # Temporary file path
                
                # Open the taf file and temporary file
                try:
                    with open(file_path, 'r') as file, open(temp_write_path, 'w') as temp_file:
                        print(f"Reading TAF file: {file_path}") # Print to console for debugging
                        
                        # Iterate over every line in the file
                        for line in file:
                            if re.search(geo_pattern, line):  # Find matches to the pattern
                                old_ver = re.search(version_pattern, line).group(1)
                                line = re.sub(version_pattern, f"_{replace_version}.", line)  # Replace the revision
                                print("Found match")
                                found_indicator = True
                                
                            temp_file.write(line)  # Write the line to the temporary file
                except FileNotFoundError:
                    print("TAF file not found")
                    return False
                # Check if the file had any matches   
                if found_indicator:
                    # Determine the final path for the updated file
                    if save_dir == self.taf_dir:
                        final_path = file_path  # Overwrite the original file
                    else:
                        final_path = os.path.join(save_dir, taf_file) # Save to new directory (can be used for debugging or testing without overwriting original files)
                        
                    self.copy_tafs_to_backup(file_path) # Copy the unmodified files to a backup folder incase of accidental change
                    os.replace(temp_write_path, final_path) # Move the updated temporary file to the final path
                    self.write_change_log(taf_file, part_num, replace_version, old_ver) # Write the changed file to the log
                    
                # Remove the temp file if it doesn't get changed from the original
                else:
                    os.remove(temp_write_path)
            return False
        else:
            return True
                
    def write_change_log(self, taf_file, part_num, revision, old_ver):
        """Writes an entry to the change log"""
        log_file_path = os.path.join(self.current_backup_dir, 'change_log.txt')
        with open(log_file_path, 'a') as log_file:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"{timestamp} - 'Modified: {taf_file} - Part Number: {part_num} - New Revision: {revision} - Old Revision: {old_ver}'\n") # Writes the date, time, taf, part, and new revision to the log file