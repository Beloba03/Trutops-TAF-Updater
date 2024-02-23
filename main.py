import re
import os
class ConfigManager:
    def __init__(self, file_path):
        self.file_path = file_path
    def load_config(self):
        """Open the config file and return the contents"""
        with open(self.file_path, 'r') as file:
            return file.read()
    def get_geo_dir(self):
        """Gets the GEO directory for the configuration"""
        config = self.load_config()
        return re.findall(r"GEO_DIR: (.*)$", config)
    def get_taf_dir(self):
        """Gets the TAF directory from the configuration"""
        config = self.load_config()
        return re.findall(r"TAF_DIR: (.*)$", config)
    
class FileManager:
    def __init__(self, taf_dir, geo_dir):
        self.taf_dir = taf_dir
        self.geo_dir = geo_dir
        self.geo_list = [file for file in os.listdir(self.geo_dir) if file.endswith('.GEO')] # Get the list of GEO files (only needs to run once at init to save time)
    def search_for_tafs(self):
        """Search directory for .TAF files"""
        try:
            return [file for file in os.listdir(self.taf_dir) if file.endswith('.TAF')] # Get all TAF files
        except FileNotFoundError:
            print("TAF directory not found")
            exit(1)
        except PermissionError:
            print("Can't search for .TAF files in this directory due to lack of permission")
            exit(1)
    def search_for_geo(self, geo_name):
        """Searches for a geo file that matches the given name"""
        for name in self.geo_list: # Iterate through the list of GEO files to check if the part exists
            if name.contains(geo_name):
                return True
        return False
    def read_and_update_taf_files(self, part_num, replace_version, taf_files = None, save_dir = None):
        """Reads each .TAF file, updates lines matching a pattern, and writes changes back."""
        part_num_escaped = re.escape(part_num)  # Convert any special characters to characters that are safe to use in regex pattern
        geo_pattern = r"\\{part_num_escaped}\.GEO"  # Pattern to match the GEO file name
        
        if taf_files is None:
            taf_files = self.search_for_tafs()
        if save_dir is None:
            save_dir = self.taf_dir

        for taf_file in taf_files:
            file_path = os.path.join(self.taf_dir, taf_file)
            temp_write_path = file_path + '.tmp'  # Temporary file path
            
            with open(file_path, 'r') as file, open(temp_write_path, 'w') as temp_file:
                for line in file:
                    if re.search(geo_pattern, line):  # Find matches to the pattern
                        line = re.sub(r"_(.*?)\.", f"_{replace_version}.", line)  # Replace the version
                    temp_file.write(line)  # Write the line to the temporary file
            
            # Replace the original file with the updated temporary file
            os.replace(temp_write_path, file_path)  # This overwrites the original file with the updated content

def main():
    config = ConfigManager('config.txt')
    geo_dir = config.get_geo_dir()
    taf_dir = config.get_taf_dir()
    file_manager = FileManager(taf_dir, geo_dir)
    taf_files = file_manager.search_for_tafs()
    part_number = input('Enter the part number to search for: ')
    new_revision = input("Please enter the new revision: ")
    file_manager.read_and_update_taf_files(input,part_number, new_revision, None, "\\")
    
if __name__ == "__main__":
    main()