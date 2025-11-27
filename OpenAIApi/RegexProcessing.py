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
section_regex = re.compile(r"\* (.+)")
subsection_regex = re.compile(r"\s*([a-z]\..+)")

result_dict = {}
current_section = None

# print results
for line in openai_result.split("\n"):
    section_match = section_regex.match(line)
    subsection_match = subsection_regex.match(line)

    if section_match:
        current_section = section_match.group(1)
        result_dict[current_section] = []
    elif subsection_match and current_section is not None:
        result_dict[current_section].append(subsection_match.group(1))

print(result_dict)