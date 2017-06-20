import json

nodes = {}

# Add a relationship 'reltype' between a 'source' node and a 'target' node
# The relationship is added only to the 'source' node
# The same relationship in the target has been already computed or it will be computed later
def add(source, target, reltype):
  # The node already exists
  if source in nodes:
    # The relationship has been already created
    # and the target has been not yet appended
    if reltype in nodes[source] and not target in nodes[source][reltype]:
      nodes[source][reltype].append(target)
    else:
      nodes[source][reltype] = [target]
  # Add the node to the index
  else:
    nodes[source] = {
      "character": source,
      reltype: [target]
    }

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

with open('graph.json', 'w') as output:
  output.write(json.dumps(nodes.values()))
