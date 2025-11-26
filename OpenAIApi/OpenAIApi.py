import re;

# suppose this is an Open's AI response
openai_result = '''
* Introduction
  a. Explanation of data engineering
  b. Importance of data engineering in today's data driven world
* Efficient Data Management
  a. Definition of data management
  b. How data engineering helps in efficient data management
* Conclusion
  a. Importance of data engineering in the modern business world
  b. Future of data engineering and its impact on the data ecosystem
'''

# regex patterns
heading_pattern = r'\* (.+)'
subheading_pattern = r'\s+[a-z]\. (.+)'

# extract headings and subheadings
headings = re.findall(heading_pattern, openai_result)
subheadings = re.findall(subheading_pattern, openai_result)

# print results
print("Headings:\n")
for heading in headings:
    print(f"* {heading}")

print("\nSubheadings:\n")
for subheading in subheadings:
    print(f"* {subheading}")