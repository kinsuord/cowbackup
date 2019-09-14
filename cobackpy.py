import fnmatch
import os
from os.path import join
import yaml
import shutil
import datetime

#def filt(files, dirs, rule):
#    pass
#    
#def backup(filtered_files, filtered_dirs, rule):
#    pass

def backup(in_path, out_path):
    if os.path.isfile(out_path):
        if os.path.getmtime(in_path) > os.path.getmtime(out_path):
            shutil.copyfile(in_path, out_path)
            with open(logfile, 'a') as f:
                f.write('modify file: {}\n'.format(in_path))
    else:
        if not os.path.isdir(os.path.split(out_path)[0]):
            os.makedirs(os.path.split(out_path)[0])
        shutil.copyfile(in_path, out_path)
        with open(logfile, 'a') as f:
            f.write('new file: {}\n'.format(in_path))

logfile = ''

if __name__ == '__main__':
    with open('setting.yaml', 'r') as f:
        cfg = yaml.load(f, yaml.BaseLoader)

    logfile = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.log')
    for i in range(len(cfg['include'])):
        if cfg['include'][i][0] == '.':
            cfg['include'][i] = join(cfg['start_folder'],cfg['include'][i][1:])
    for i in range(len(cfg['exclude'])):
        if cfg['exclude'][i][0] == '.':
            cfg['exclude'][i] = join(cfg['start_folder'],cfg['exclude'][i][1:])
    

    for root, dirs, files in os.walk(cfg['start_folder'], topdown=True):   
        for file in files:
            match = True
            for filter in cfg['exclude']:
                if fnmatch.fnmatch(join(root,file), filter):
                    match = False
            if match == False:
                continue
            
            match = False
            for filter in cfg['include']:
                if fnmatch.fnmatch(join(root,file), filter):
                    match = True
            if match==True:
                root_clip = root.split('/')[1]
                backup(join(root, file), join(cfg['target'], root_clip, file))
#                with open('test.txt', 'a') as f:
#                    f.write(join(root,file)+'\n')

#if __name__ == '__main__':
#    with open('setting.yaml', 'r') as f:
#        cfg = yaml.load(f, yaml.BaseLoader)
##    walk(cfg['start_floder'], None)
##    {'root' 'include' 'exclude'}
#    stack = [None]
#    
#    # include 直接取代
#    # exclude 會多覆蓋規則
#    # target 直接取代
#    
#    for root, dirs, files in os.walk(cfg['start_floder'], topdown=True):
#        if 'cobackpy.yaml' in files:
#            with open(join(root, 'cobackpy.yaml'), 'r') as f:
#                cfg = yaml.load(f, yaml.BaseLoader)
#            
#            if stack[-1] == None:
#                stack.append({
#                        'root': root,
#                        'cfg': cfg})
#            else:
#                pre_rule = stack[-1]
#                if 'include' not in cfg:
#                    cfg['include'] = pre_rule['include']
#                
#                
#    
#        if root.find(stack[-1]['root'])<0:
#            print(stack[-1]['root'])
#            stack.pop()
#        rule = stack[-1]
#        filtered_files, filtered_dirs = filt(files, dirs, rule)
#        backup(filtered_files, filtered_dirs)
        
#        print(root)
#        i += 1
#        if i > 50:
#            break
#        for name in files:
#            print(os.path.join(root, name))
#        for name in dirs:
#            print(os.path.join(root, name))