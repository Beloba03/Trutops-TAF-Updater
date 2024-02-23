import re


# FINAL CODE
class ConfigManager:
    def __init__(self, file_path):
        self.file_path = file_path
    def load_config(self):
        with open(self.file_path, 'r') as file:
            return file.read()
    def get_geo_dir(self):
        config = self.load_config()
        return re.findall(r"GEO_DIR: (.*)$", config)
    def get_taf_dir(self):
        config = self.load_config()
        return re.findall(r"TAF_DIR: (.*)$", config)
class FileManager:
    def __init__(self, taf_dir, geo_dir):
        self.taf_dir = taf_dir
        self.geo_dir = geo_dir
        
        
        
# TEST CODE:
taf_matches = []
file_path = 'C:\\Users\\benba\OneDrive\\Desktop\\Python GEO TAF\\JOB-TAF\\BCL TEMP.TAF'
temp_write_path = 'output.txt'
geo_pattern = r"\\[A-Za-z]{3}.*?\.GEO"
file_hold = []

replace_version = 'A'
with open(file_path, 'r') as file:
    for line in file:
        if re.findall(geo_pattern, line):
            line = re.sub(r"_(.*?)\.", f"_{replace_version}.", line)
            taf_matches.append(line)
        file_hold.append(line)
with open(temp_write_path, 'w') as file:
    for line in file_hold:
        file.write(line)