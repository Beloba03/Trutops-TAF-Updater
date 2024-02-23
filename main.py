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
        matches = re.findall(r'GEO_DIR: "(.*)"', config)
        print(f"GEO: {matches[0]}")
        return matches[0]   
    def get_taf_dir(self):
        """Gets the TAF directory from the configuration"""
        config = self.load_config()
        matches = re.findall(r'TAF_DIR: "(.*)"', config)
        print(f"TAF: {matches[0]}")
        return matches[0]
    
class FileManager:
    def __init__(self, taf_dir, geo_dir):
        self.taf_dir = taf_dir
        self.geo_dir = geo_dir
        self.geo_list = [file for file in os.listdir(self.geo_dir) if file.endswith('.GEO')] # Get the list of GEO files (only needs to run once at init to save time)
    def search_for_tafs(self):
        """Search directory for .TAF files"""
        try:
            taf_list = [file for file in os.listdir(self.taf_dir) if file.endswith('.TAF')] # Get all TAF files
            print(f"TAFS: {taf_list}")
            return taf_list
        except FileNotFoundError:
            print("TAF directory not found")
            exit(1)
        except PermissionError:
            print("Can't search for .TAF files in this directory due to lack of permission")
            exit(1)
    def search_for_geo(self, geo_name):
        """Searches for a geo file that matches the given name"""
        for name in self.geo_list: # Iterate through the list of GEO files to check if the part exists
            if name in geo_name:
                return True
        return False
    def read_and_update_taf_files(self, part_num, replace_version, taf_files = None, save_dir = None):
        """Reads each .TAF file, updates lines matching a pattern, and writes changes back."""
        part_num_escaped = re.escape(part_num)  # Convert any special characters to characters that are safe to use in regex pattern
        geo_pattern = rf"{part_num_escaped}_.*\.GEO"  # Pattern to match the GEO file name
        
        if taf_files is None:
            taf_files = self.search_for_tafs()
        if save_dir is None:
            save_dir = self.taf_dir

        for taf_file in taf_files:
            found_indicator = False  # Indicator for whether the TAF was changed
            file_path = os.path.join(self.taf_dir, taf_file)
            temp_write_path = file_path + '.tmp'  # Temporary file path
            
            with open(file_path, 'r') as file, open(temp_write_path, 'w') as temp_file:
                print(f"Reading taf file: {file_path}")
                for line in file:
                    if re.search(geo_pattern, line):  # Find matches to the pattern
                        line = re.sub(r"_(.*?)\.", f"_{replace_version}.", line)  # Replace the version
                        print("Found match")
                        found_indicator = True
                    temp_file.write(line)  # Write the line to the temporary file
            if found_indicator:
                # Determine the final path for the updated file
                if save_dir == self.taf_dir:
                    final_path = file_path  # Overwrite the original file
                else:
                    # Save to new directory (can be used for debugging or testing without overwriting original files)
                    final_path = os.path.join(save_dir, taf_file)

                # Move the updated temporary file to the final path
                os.replace(temp_write_path, final_path)

def main():
    config = ConfigManager('config.txt')
    geo_dir = config.get_geo_dir()
    taf_dir = config.get_taf_dir()
    file_manager = FileManager(taf_dir, geo_dir)
    taf_files = file_manager.search_for_tafs()
    part_number = input('Enter the part number to search for: ')
    new_revision = input("Please enter the new revision: ")
    file_manager.read_and_update_taf_files(part_number, new_revision, None, "TAF_Temp")
    
if __name__ == "__main__":
    main()