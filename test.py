# Example string with underscores
pdf_part_with_underscore = "example_string_with_underscore"
# Example string without underscores
pdf_part_without_underscore = "examplestringwithoutunderscore"

# Splitting at the last underscore
split_with = pdf_part_with_underscore.rsplit('_', 1)
split_without = pdf_part_without_underscore.rsplit('_', 1)

# Output results
print("With underscore:", split_with)
print("Without underscore:", split_without)
