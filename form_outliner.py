import argparse
import json
from operator import itemgetter

# converts Eclipse form Json to a human-readable text outline
# 
# bugs:
# puts collection fields after normal fields in each section (ignores row number)
# ignores column titles for collection fields
# number input fields do not have a subType - needs special case

parser = argparse.ArgumentParser()

parser.add_argument('form_json', help="Eclipse form config json file")

args = parser.parse_args()

def identify_rule(item):
  # finds name of form rule, or GUID of global rule, applied to this item
  # returns None if there is no visibility rule set
  vis_id = item.get('visibilityRuleId', None)
  if not vis_id:
    return None
  # list the names of form rules with matching IDs (will be 0 or 1 name)
  matching_rules = [r['name'] for r in rules if r['definitionId'] == vis_id]
  if len(matching_rules) > 0:
  # if the rule was found in the form rules, return its name
    return matching_rules[0]
  else:
  # if no name was found, assume the GUID refers to a global rule
    return f"global rule {vis_id}"
    
def collapse_section(section):
  # returns a list of controls in a section
  #
  # sections contain a list of rows and a list of groups
  # groups (repeatable collections) also contain a list of rows
  # each row contains a list of columns
  # columns contain a list of controls
  #
  # todo: put rows into correct order, instead of group rows last
  for row in section['rows']:
    for column in row['columns']:
      for control in column['controls']:
        yield control
  for group in section['groups']:
    for row in group['rows']:
      for column in row['columns']:
        for control in column['controls']:
          yield control
          
def parse_choices(control):
  # convert json choices back into Form Designer format
  for choice in control['choices']:
    if choice.get('selectedByDefault', False):
      default = " *"
    else:
      default = ""
    yield f"{choice['label']}:{choice['value']}{default}"
    
def mandatory_type(control):
  # shows mandatory status of a control if set
  # if no data found, or set to NOT_MANDATORY, returns None
  if 'validation' not in control:
    return None
  validation = control['validation']
  if 'mandatory' not in validation:
    return None
  mandatory = validation['mandatory']
  if mandatory == 'NOT_MANDATORY':
    return None
  return mandatory
  


# load file specified in command line
with open(args.form_json) as file:
  form = json.load(file)
  
  # print name and version
  print(form['name'])
  print(f"Version: {form['version']}")

  # list form rules
  rules = form['rules']
  print("\nForm rules:")
  for r in sorted(rules, key=itemgetter('name')):
    print(f"  {r['name']}")
  
  # print outline of pages and sections
  pages = form['pages']
  print("\nForm outline:")
  for page in pages:
    rule = identify_rule(page)
    if rule:
      print(f"  {page['title']} (Visibility rule: {rule})")
    else:
      print(f"  {page['title']}")
      
    for section in page['sections']:
      rule = identify_rule(section)
      if rule:
        print(f"    {section['title']} (Visibility rule: {rule})")
      else:
        print(f"    {section['title']}")
      

  print() # spacing
  print("Detailed form outline:")
  for page in pages:
    print() # spacing
    print(f"Page:\t{page['title']}")
    print(f"Name:\t{page['name']}")
    rule = identify_rule(page)
    if rule:
      print(f"Visibility:\t{rule}")
    
    for section in page['sections']:
      print() # spacing
      print(f"Section:\t{section['title']}")
      print(f"Name:\t{section['name']}")
      rule = identify_rule(section)
      if rule:
        print(f"Visibility:\t{rule}")
           
      for control in collapse_section(section):
        print() # spacing
        if 'label' in control and 'value' in control['label']:
          print(f"Field:\t{control['label']['value']}")
        print(f"Name:\t{control.get('name', '<none>')}")
        print(f"Type:\t{control.get('subType', '<none>')}")
        if 'choices' in control:
          print("Choices:")
          for choice in parse_choices(control):
            print(f"\t\t{choice}")
        group_scope = control.get('groupScope', False)
        if group_scope:
          print(f"Group scope:\tTrue")
        mandatory = mandatory_type(control)
        if mandatory:
          print(f"Mandatory:\t{mandatory}")
        rule = identify_rule(control)
        if rule:
          print(f"Visibility:\t{rule}")

  print()
  print("Form outliner v0.3")