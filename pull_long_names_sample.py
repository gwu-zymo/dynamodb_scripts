#load the table of content
#using full scientific name of species
import os

#all_run: Run_Number (mdXXXX):date
#all_ID: Tube_ID:Run_Number (only the newest run for each sample, if table in order)
all_run = {}
all_ID = {}
all_metadata = {}
all_sample = {}

inp = open('TOC_4_10_23_mod.txt', encoding = 'utf-8')
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
        if not line.startswith('#'):
            line_split = line.strip('\n').split('\t')
            id = line_split[1]
            ct = [] 
            for key in line_split[2:7]:
                try:
                    a = float(key)
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

for run_ID in all_run:
    folder = '%s.%s.zymo' % (run_ID, all_run[run_ID])
    zip_file = 's3://midog/Projects/%s/analysis/%s.zip' % (run_ID, folder)
    try:
        os.system('aws s3 cp %s .' % zip_file)
        os.system('unzip %s.zip' % folder)

        read_abd_file('./%s/midog.a.Bac16Sv13/taxa_plots/sorted_otu_L7.txt' % folder)
        read_abd_file('./%s/midog.b.FungiITS/taxa_plots/sorted_otu_L7.txt' % folder)

        try:
            read_abs_tally('./%s/midog.a.Bac16Sv13/ABS/1.species.abs.tsv' % folder)
        except:
            print('no abs')
        try:
            read_abd_file('./%s/midog.c.AMR/taxa_plots/sorted_otu_L7.txt' % folder)
        except:
            print('no .c')
        try:
            read_abd_file('./%s/midog.d.AMR/taxa_plots/sorted_otu_L7.txt' % folder)
        except:
            print('no .d')
        try:
            read_abd_file('./%s/midog.k.AMRm/taxa_plots/sorted_otu_L7.txt' % folder)
        except:
            print('no .k')
        try:
            update_ct('./%s/qPCR/extracted_ct_values.csv' % folder)
        except:
            print('no ct')
        
        os.system('rm *.zip')
        os.system('rm -r md*')
    except:
        print('zip file not found')
        oup.write(zip_file + '\n')
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
