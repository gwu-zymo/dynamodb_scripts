#modify TOC, remove any mid-line change line signs, any non-numeric in numeric columns

float_list = ["ct_V1V3", "ct_ITS", "ct_AMR1", "ct_AMR2", "ct_AMRm", "Age_Years"]

inp = open('TOC_4_10_23.txt', 'r')
oup = open('TOC_4_10_23_mod.txt', 'w')
line = inp.readline()
oup.write(line)
header = line.strip('\n').split('\t')
lines = inp.readlines()
lines_merged = []
tmp_line = ''
for i in range(len(lines)-1, -1, -1):
  if 'RUN' not in lines[i]:
    tmp_line = lines[i].strip('.\n') + tmp_line
  else:
    lines_merged.append(lines[i].strip('.\n') + tmp_line)
    tmp_line = ''

lines_merged_split = []
for line in lines_merged:
  split_line = line.split('\t')
  lines_merged_split.append(line.split('\t'))
  if len(split_line) != 39:
    print('line error!! not right number of tabs', len(split_line), split_line[8])

print('total lines after mid line change line sign removal:', len(lines_merged))

#manually fix the errors and then continue
#in some instances there are an unexpected '\t' in front of phone number
#this is impossible to anticipate
                            
float_i = []
for i in range(0, len(header)):
  if header[i] in float_list:
    float_i.append(i)

lines_merged_split_m = []
for sample in lines_merged_split:
  for i in range(0, len(sample)):
    if i in float_i:
      if sample[i] != '':
        try:
          tmp = float(sample[i])
        except:
          sample[i] = ''
  lines_merged_split_m.append(sample)
  oup.write('\t'.join(sample) + '\n')

inp.close()
oup.close()

                            
                            
                            
                            
                      
