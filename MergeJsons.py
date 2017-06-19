files={'aleja', 'arash', 'gin','donald','atsushi','sofia','gero','carlo','david'}
files={'arash', 'gin','donald','atsushi','carlo','david'}

with open('../results/super.json', 'w') as outfile:
    contents=''
    for sub in files:
        contents+=open('../results/'+sub+'.json').read()
    contents=contents.replace('][',',\n')
    outfile.write(contents)