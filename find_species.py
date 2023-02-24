#in selected_samples.csv, find the speices that contain 'Malassezia'

all = {}
inp = open('selected_samples.csv', 'r')
line = inp.readline()
header = line.strip('\n').split(',')
line = inp.readline()
while line:
  ll = line.strip('\n').split(',')
  id = ll[header.index('Internal_Sample_ID')]
  all[id] = {}
  for spe in header:
    if 'Malassezia' in spe:
      all[id][spe] = ll[header.index(spe)]
  line = inp.readline()
inp.close()

count = {}
for sample in all:
  for key in all[sample]:
    if not key in count:
      count[key] = 0
    if all[sample][key] != '':
      if float(all[sample][key]) > 0:
        count[key] = count[key] + 1

for species in count:
  print(species, count[species])
