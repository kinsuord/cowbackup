import os
import fnmatch
import argparse
from tqdm import tqdm
import yaml
import shutil
import datetime

def match_filter(path, filter):
    if filter == None:
        return True
    for rule in filter['must_include']:
        if fnmatch.fnmatch(path, rule):
            return True
    for rule in filter['exclude']:
        if fnmatch.fnmatch(path, rule):
            return False
    for rule in filter['include']:
        if fnmatch.fnmatch(path, rule):
            return True
    return False

def get_file_list(dir, filter):
    file_dict = dict()
    
    for root, dirs, files in os.walk(dir):
        for file in files:
            path = os.path.join(root, file)
            if match_filter(path, filter):
                file_dict[path] = True

    return file_dict

if __name__ == '__main__':
    # args
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file", help="task setting in .yaml")
    args = parser.parse_args()
    
    # tasks, filters
    with open(args.task_file, 'r') as f:
         cfg = yaml.load(f, yaml.BaseLoader)
    tasks = cfg['tasks']
    filters = dict()
    for filter in cfg['filters']:
        filters[filter['name']] = dict()
        for rule in ['include', 'exclude', 'must_include']:
            if not rule in filter:
                filters[filter['name']][rule] = []
            else:
                filters[filter['name']][rule] = filter[rule]
    
    for task in tasks:
        print('Backuping task {} ...'.format(task['name']))
        # making filter_list
        for rule in ['include', 'exclude', 'must_include']:
            if not rule in task['filter']:
                task['filter'][rule] = []
            if 'pre_defined' in task['filter']:
                for defined_fliter in task['filter']['pre_defined']:
                    task['filter'][rule] = task['filter'][rule] + filters[defined_fliter][rule]

        source_files = get_file_list(task['source'], task['filter'])
        target_files = get_file_list(task['target'], None)
        print('Source files: {} Target files: {}'.format(len(source_files), len(target_files)))
        
        # List(Operation)
        ops = []
        for source in source_files:
            target = source.replace(task['source'], task['target'])
            if not target in target_files:
                ops.append({
                        'method': 'new',
                        'target': target,
                        'source': source})
            elif os.path.getmtime(source) > os.path.getmtime(target):
                ops.append({
                    'method': 'update',
                    'target': target,
                    'source': source})
        for target in target_files:
            if not target in source_files:
                ops.append({
                    'method': 'delete',
                    'target': target,
                    'source': None})
    
        print('Copying and deleting ...')
        pbar = tqdm(ops)
        for op in pbar:
            if op['method'] == 'new' or op['method'] == 'update':
                pbar.set_description("{} {} ...".format(op['method'], op['target']))
                target_dir = os.path.split(op['target'])[0]
                if not os.path.isdir(target_dir):
                    os.makedirs(target_dir)
                shutil.copyfile(op['source'], op['target'])
            elif op['method'] == 'delete':
                os.remove(op['target'])
                
        # writing log file:
        logfile = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.log')
        with open(os.path.join('./log', logfile), 'a') as f:
            for op in ops:
                f.write('{}: {}\n'.format(op['method'], op['target']))
        
                
            

# import fnmatch
# import os
# from os.path import join
# import yaml
# import shutil
# import datetime

# #def rule(files, dirs, rule):
# #    pass
# #    
# #def backup(filtered_files, filtered_dirs, rule):
# #    pass

# def backup(in_path, out_path):
#     if os.path.isfile(out_path):
#         if os.path.getmtime(in_path) > os.path.getmtime(out_path):
#             shutil.copyfile(in_path, out_path)
#             with open(logfile, 'a') as f:
#                 f.write('modify file: {}\n'.format(in_path))
#     else:
#         if not os.path.isdir(os.path.split(out_path)[0]):
#             os.makedirs(os.path.split(out_path)[0])
#         shutil.copyfile(in_path, out_path)
#         with open(logfile, 'a') as f:
#             f.write('new file: {}\n'.format(in_path))

# logfile = ''

# if __name__ == '__main__':
#     with open('setting.yaml', 'r') as f:
#         cfg = yaml.load(f, yaml.BaseLoader)

#     logfile = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.log')
#     for i in range(len(cfg['include'])):
#         if cfg['include'][i][0] == '.':
#             cfg['include'][i] = join(cfg['start_folder'],cfg['include'][i][1:])
#     for i in range(len(cfg['exclude'])):
#         if cfg['exclude'][i][0] == '.':
#             cfg['exclude'][i] = join(cfg['start_folder'],cfg['exclude'][i][1:])
    

#     for root, dirs, files in os.walk(cfg['start_folder'], topdown=True):   
#         for file in files:
#             match = True
#             for filter in cfg['exclude']:
#                 if fnmatch.fnmatch(join(root,file), filter):
#                     match = False
#             if match == False:
#                 continue
            
#             match = False
#             for filter in cfg['include']:
#                 if fnmatch.fnmatch(join(root,file), filter):
#                     match = True
#             if match==True:
#                 root_clip = root.split('/')[1]
#                 backup(join(root, file), join(cfg['target'], root_clip, file))
# #                with open('test.txt', 'a') as f:
# #                    f.write(join(root,file)+'\n')

# #if __name__ == '__main__':
# #    with open('setting.yaml', 'r') as f:
# #        cfg = yaml.load(f, yaml.BaseLoader)
# ##    walk(cfg['start_floder'], None)
# ##    {'root' 'include' 'exclude'}
# #    stack = [None]
# #    
# #    # include 直接取代
# #    # exclude 會多覆蓋規則
# #    # target 直接取代
# #    
# #    for root, dirs, files in os.walk(cfg['start_floder'], topdown=True):
# #        if 'cobackpy.yaml' in files:
# #            with open(join(root, 'cobackpy.yaml'), 'r') as f:
# #                cfg = yaml.load(f, yaml.BaseLoader)
# #            
# #            if stack[-1] == None:
# #                stack.append({
# #                        'root': root,
# #                        'cfg': cfg})
# #            else:
# #                pre_rule = stack[-1]
# #                if 'include' not in cfg:
# #                    cfg['include'] = pre_rule['include']
# #                
# #                
# #    
# #        if root.find(stack[-1]['root'])<0:
# #            print(stack[-1]['root'])
# #            stack.pop()
# #        rule = stack[-1]
# #        filtered_files, filtered_dirs = rule(files, dirs, rule)
# #        backup(filtered_files, filtered_dirs)
        
# #        print(root)
# #        i += 1
# #        if i > 50:
# #            break
# #        for name in files:
# #            print(os.path.join(root, name))
# #        for name in dirs:
# #            print(os.path.join(root, name))