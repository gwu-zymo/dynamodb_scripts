#load the table of content
#using full scientific name of species
import os

#all_run: Run_Number (mdXXXX):date
#all_ID: Tube_ID:Run_Number (only the newest run for each sample, if table in order)
all_run = {}
all_ID = {}
all_metadata = {}
all_sample = {}

inp = open('TOC_8_23_2023.txt', encoding = 'windows-1252')
line = inp.readline()
header = line.strip('\n')
line = inp.readline()
while line:
    print(line[:100])
    line_split = line.strip('\n').split('\t')
    print(line_split[8])
    all_sample[line_split[8]] = ''
    run_ID = line_split[8].split('_')[0]
    all_run[run_ID] = line_split[6]
    all_ID[line_split[9]] = run_ID
    all_metadata[line_split[9]] = line.strip('\n').replace(',', '-')
    line = inp.readline()
inp.close()

#pull abundance file from s3 according to sample_ID
all_abd = {}
all_spe = {}

def read_abd_file(file):
    inp = open(file, 'r')
    line = inp.readline()
    sample_order = line.strip('\n').split('\t')[1:]
    for sample in sample_order:
        if sample not in all_abd:
            all_abd[sample] = {}
    line = inp.readline()
    while line:
        line_split = line.strip('\n').split('\t')
        species = line_split[0]
        all_spe[species] = ''
        for i in range(0, len(sample_order)):
            all_abd[sample_order[i]][species] = line_split[i + 1]
        line = inp.readline()
    inp.close()

def read_abs_tally(file):
    inp = open(file, 'r')
    line = inp.readline()
    sample_order = line.strip('\n').split('\t')[1:]
    for sample in sample_order:
        if sample not in all_abd:
            all_abd[sample] = {}
        all_abd[sample]['total_abs_in_cp_nr'] = 0
    line = inp.readline()
    while line:
        line_split = line.strip('\n').split('\t')
        list_f = [float(num) for num in line_split[1:]]
        for i in range(0, len(sample_order)):
            all_abd[sample_order[i]]['total_abs_in_cp_nr']+=list_f[i]
        line = inp.readline()
    inp.close()

def update_ct(file):
    inp = open(file, 'r')
    line = inp.readline()
    while line:
        if not line.startswith('InternalID'):
            line_split = line.strip('\n').split(',')
            id = line_split[1]
            ct = [] 
            for key in line_split[2:6]:
                try:
                    a = float(key)
                    ct.append(key)
                except:
                    ct.append('')
            try: 
                a = float(line_split[12])
                ct.append(key)
            except:
                ct.append('')
            
            if id in all_metadata:
                old = all_metadata[id].split('\t')
                old[0:5] = ct
                all_metadata[id] = '\t'.join(old)
        line = inp.readline()
    inp.close()
            
    
def modify_taxonomy_name(species):
    split = species.split(';')
    header = [split[0][0:4].replace('__', '_')]
    tail = []
    count = 0
    for i in range(len(split)-1, -1, -1):
        if (not 'Other' in split[i]) and (not 'NA' in split[i]) and (not 'bacterium' in split[i]):
            tail.append(split[i].replace('__', '_'))
            count = count + 1
        if count == 2:
            break

    tail.reverse()
    new_species = '_'.join(header + tail)
    #return(new_species)
    return(species)
  
oup = open('zip_not_found.txt', 'w')

total_run = {}
for sample in all_sample:
    folder = 's3://midog/database_by_samples/runs/%s/%s' % (sample.split('_')[0], sample.split('_')[1])
    total_run[sample.split('_')[0]] = ''
    
    try:
        os.system('aws s3 cp %s/a/%sa.taxa.abun.tsv .' % (folder, sample))
        read_abd_file('%sa.taxa.abun.tsv' % sample)
    except:
        print('no a')
    try:
        os.system('aws s3 cp %s/b/%sb.taxa.abun.tsv .' % (folder, sample))
        read_abd_file('%sb.taxa.abun.tsv' % sample)
    except:
        print('no b')
    try:
        os.system('aws s3 cp %s/c/%sc.taxa.abun.tsv .' % (folder, sample))
        read_abd_file('%sc.taxa.abun.tsv' % sample)
    except:
        print('no c')
    try:
        os.system('aws s3 cp %s/d/%sd.taxa.abun.tsv .' % (folder, sample))
        read_abd_file('%sd.taxa.abun.tsv' % sample)
    except:
        print('no d')
    try:
        os.system('aws s3 cp %s/k/%sk.taxa.abun.tsv .' % (folder, sample))
        read_abd_file('%sk.taxa.abun.tsv' % sample)
    except:
        print('no k')

for folder in total_run:
    try:
        os.system('aws s3 cp s3://midog/database_by_samples/runs/%s/Ctvalues.tsv ./' % folder)
        os.system('mv Ctvalues.tsv %s_Ctvalues.tsv' % folder)
        update_ct('%s_Ctvalues.tsv' % folder)
    except:
        print('no ct')
        
    os.system('rm *.tsv')
oup.close()


oup = open('abundance.csv', 'w')
all_spe_list = all_spe.keys()
all_spe_write = []
n = 1
for species in all_spe_list:
#    split = species.split(';')
#    new_spe = '_'.join(split[0:1] + split[-2:]).replace('Bacteria', 'B').replace('Fungi', 'F').replace('Function', '')
    new_spe = modify_taxonomy_name(species)
    if len(new_spe) > 256:
        print(new_spe + ' name too long!')
    if new_spe in all_spe_write:
        print(new_spe + ' already in the list!!!')
        new_spe = new_spe + str(n)
        n = n + 1
    all_spe_write.append(new_spe)


oup.write(header.replace('\t', ',') + ',%s\n' % ','.join(all_spe_write))
for sample in all_metadata:
    if sample in all_abd:
        oup.write(all_metadata[sample].replace('\t', ','))
        for species in all_spe_list:
            if species in all_abd[sample]:
                if all_abd[sample][species] != '0' and all_abd[sample][species] != '0.0':
                    oup.write(',' + all_abd[sample][species])
                else:
                    oup.write(',')
            else:
                #oup.write(',0')
                oup.write(',')
        oup.write('\n')
oup.close()
