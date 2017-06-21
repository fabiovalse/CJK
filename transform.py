# -*- coding: utf-8 -*-
import json
import codecs

nodes = {}

# Add a relationship 'reltype' between a 'source' node and a 'target' node
# The relationship is added only to the 'source' node
# The same relationship in the target has been already computed or it will be computed later
def add(source, target, reltype):
  # The node already exists
  if source in nodes:
    # The relationship has been already created
    # and the target has been not yet appended
    if reltype in nodes[source]:
      if not target in nodes[source][reltype]:
        nodes[source][reltype].append(target)
    else:
      nodes[source][reltype] = [target]
  # Add the node to the index
  else:
    nodes[source] = {
      "character": source,
      reltype: [target]
    }

def update(character, field, new_value):
  nodes[character][field] = new_value

# Read makemeahanzi dictionary file
with open('makemeahanzi/dictionary.txt', 'r') as dictionary:
  for line in dictionary:
    d = json.loads(line)

    # If the node is not in the index, add it
    if not d['character'] in nodes:
      nodes[d['character']] = {
        "character": d['character']
      }

    # In all cases set its properties
    nodes[d['character']]['radical'] = d['radical']
    nodes[d['character']]['pinyin'] = d['pinyin'][0] if len(d['pinyin']) > 0 else ''
    nodes[d['character']]['definition'] = map(lambda x: x.strip(), d['definition'].split(';')) if 'definition' in d else []
    nodes[d['character']]['decomposition'] = d['decomposition'] if 'decomposition' in d else ''
    nodes[d['character']]['contains'] = list(d['decomposition']) if 'decomposition' in d else []
    nodes[d['character']]['etymology'] = d['etymology'] if 'etymology' in d else {}

    # Add inverse relationships from decomposition
    if 'decomposition' in d:
      for c in d['decomposition']:
        add(c, d['character'], 'is_contained_by')

    # Add inverse relationship from radical
    add(d['radical'], d['character'], 'is_radical_of')

# Read makemeahanzi graphics file
with open('makemeahanzi/graphics.txt', 'r') as graphics:
  for line in graphics:
    d = json.loads(line)

    nodes[d['character']]['strokes'] = d['strokes']
    nodes[d['character']]['medians'] = d['medians']

# Read cjkvi-ids file
with codecs.open('cjkvi-ids/ids.txt', 'r', 'utf-8') as ids:
  for (i,line) in enumerate(ids):
    # skip header
    if i > 2 and line[0:2] != ';;':
      fields = line.split('\t')
      character = fields[1]

      if character in nodes:
        # decomposition coming from cjkvi-ids file
        new_decomposition = fields[2].replace('\n', '')
        # decomposition coming from makemeahanzi dictionary file
        old_decomposition = nodes[fields[1]]['decomposition'] if 'decomposition' in nodes[fields[1]] else ''
        # missing characters are represented as '？' in the makemeahanzi dictionary file
        missing = ('？').decode("utf-8")
        
        # the old decomposition is missing
        if character != new_decomposition and old_decomposition == missing:
          update(fields[1], 'decomposition', new_decomposition)
          update(fields[1], 'contains', list(new_decomposition))
          # Add inverse relationships from decomposition
          for c in list(new_decomposition):
            add(c, character, 'is_contained_by')

        # Particular case of one character
        elif character != new_decomposition and len(old_decomposition) == 1 and new_decomposition != old_decomposition:
          update(fields[1], 'decomposition', new_decomposition)
          update(fields[1], 'contains', list(new_decomposition))
          # Add inverse relationships from decomposition
          for c in list(new_decomposition):
            add(c, character, 'is_contained_by')

        # The old decomposition is partial
        elif character != new_decomposition and len(old_decomposition) > 1 and missing in old_decomposition:
          update(fields[1], 'decomposition', new_decomposition)
          update(fields[1], 'contains', list(new_decomposition))
          # Add inverse relationships from decomposition
          for c in list(new_decomposition):
            add(c, character, 'is_contained_by')

# Write output JSON
with open('graph.json', 'w') as output:
  output.write(json.dumps(nodes.values()))
