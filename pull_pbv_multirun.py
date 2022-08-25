#load the table of content, when there is multiple zip files, take the one with the newest date
import os, sys

#all_run: Run_Number(pbvXXXX):date
#all_ID: tube_ID_date:Run_Number (only the newest run for each sample, if table in order)
#all_metadata: tube_ID: whole line
#all_prev: previous ID: tube_ID
all_run = {}
all_ID = {}
all_metadata = {}
all_prev = {}

inp = open('TOC_pbv.txt', encoding = 'windows-1252')
line = inp.readline()
header = line.strip('\n')
line = inp.readline()
while line:
    print(line[:100])
    line_split = line.strip('\n').split('\t')
    print(line_split[1])
    run_ID = line_split[2].split('_')[0]
    all_run[run_ID] = line_split[0]
    tube_ID = line_split[3].replace('-', '.').replace('_', '.')
    all_ID[tube_ID] = run_ID
    all_metadata[tube_ID] = line.strip('\n').replace(',', '-')
    all_prev[line_split[5]] = tube_ID
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
    return(new_species)

oup = open('zip_not_found.txt', 'w')

for run_ID in all_run:
    folder = '%s.%s.zymo' % (run_ID, all_run[run_ID])
    zip_file = 's3://precisionbiome/PrecisionBIOME_Vaginal/Projects/%s/analysis/%s.zip' % (run_ID, folder)
    file_path = 's3://precisionbiome/PrecisionBIOME_Vaginal/Projects/%s/analysis/' % (run_ID)
    try:
        os.system('aws s3 sync %s .' % file_path)
    except:
        oup.write(zip_file + '\n')
        
    r_date = []
    for f in os.listdir('./'):
        if f.endswith('.zymo.zip'):
            nd = ''
            try:
                nd = int(f.split('.')[1])
            except:
                pass
            if nd != '':
                r_date.append(int(nd))
    if len(r_date) > 0:
        n_date = str(max(r_date))
        folder = '%s.%s.zymo' % (run_ID, n_date)
            
    try:
        os.system('unzip %s.zip' % folder)

        read_abd_file('./%s/midog.a.Bac16Sv13/taxa_plots/sorted_otu_L7.txt' % folder)
        read_abd_file('./%s/midog.b.FungiITS/taxa_plots/sorted_otu_L7.txt' % folder)

        try:
            read_abd_file('./%s/midog.f.AMR/taxa_plots/sorted_otu_L7.txt' % folder)
        except:
            print('no .f')
            
        try:
            read_abd_file('./%s/midog.f.AMRm/taxa_plots/sorted_otu_L7.txt' % folder)
        except:
            print('no .fm')
            
        try:
            read_abd_file('./%s/midog.g.VIRUS/taxa_plots/sorted_otu_L7.txt' % folder)
        except:
            print('no .g')
            
        try:
            read_abd_file('./%s/midog.l.AMRm/taxa_plots/sorted_otu_L7.txt' % folder)
        except:
            print('no .l')

        
    except:
        print('zip file not found')
        
    
    os.system('rm *.zip')
    os.system('rm -r pbv*')
oup.close()


oup = open('abundance.csv', 'w')
all_spe_list = all_spe.keys()
all_spe_write = []
n = 1
for species in all_spe_list:
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
        
    elif all_prev[sample] in all_abd:
        sample = all_prev[sample]
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

oup = open('not_found.txt', 'w')
for tube_ID in all_metadata:
    if not tube_ID in all_abd:
        oup.write(tube_ID + '\t' + all_ID[tube_ID] + '\n')
oup.close()
