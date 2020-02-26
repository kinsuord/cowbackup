import os
import fnmatch
import argparse
from tqdm import tqdm
import yaml
import shutil
import time
import datetime
import pickle

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


class Op():
    def __init__(self, target, method, source=None):
        self.method = method
        self.target = target
        self.source = source

    def __str__(self):
        return '{}: {}'.format(self.method, self.target)

    def run(self):
        if self.method == 'new' or self.method == 'update':
            target_dir = os.path.split(self.target)[0]
            if not os.path.isdir(target_dir):
                os.makedirs(target_dir)
            shutil.copyfile(self.source, self.target)
        elif self.method == 'delete':
            os.remove(self.target)

def get_file_set(dir, filter):
    file_set = set()
    
    for root, dirs, files in os.walk(dir):
        for file in files:
            path = os.path.join(root, file)
            if match_filter(path, filter):
                file_set.add(path)

    return file_set

if __name__ == '__main__':
    
    #%% set argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file", help="task setting in .yaml")
    parser.add_argument('--test', action='store_true', help="log out files but don't modify")
    args = parser.parse_args()
    
    #%% read tasks, filter
    with open(args.task_file, 'r') as f:
        cfg = yaml.load(f, yaml.SafeLoader)
    tasks = cfg['tasks']
    filters = dict()
    for filter in cfg['filters']:
        filters[filter['name']] = dict()
        for rule in ['include', 'exclude', 'must_include']:
            if not rule in filter:
                filters[filter['name']][rule] = []
            else:
                filters[filter['name']][rule] = filter[rule]

    #%% set logfile
    if args.test:
        logfile = 'test.log'
    else:
        logfile = os.path.join('log', datetime.datetime.now().strftime('%Y%m%d_%H%M%S.log'))
        if not os.path.isdir('log'):
            os.makedirs('log')
    # clear the log file
    open(logfile, "w").close()                

    #%% load record
    if os.path.isfile('record.pkl'):
        with open('record.pkl', 'rb') as f:
            record = pickle.load(f)
    else:
        record = dict()
        record['update_time'] = 0
    
    for task in tasks:
        if not task['name'] in record:
            record[task['name']] = set()

    for task in tasks:
        print('Backuping task {} ...'.format(task['name']))

        #%% making filter_list
        for rule in ['include', 'exclude', 'must_include']:
            if not rule in task['filter']:
                task['filter'][rule] = []
            if 'pre_defined' in task['filter']:
                for defined_fliter in task['filter']['pre_defined']:
                    task['filter'][rule] = task['filter'][rule] + filters[defined_fliter][rule]

        source_files = get_file_set(task['source'], task['filter'])
        target_files = get_file_set(task['target'], task['filter'])
        print('Source files: {} Target files: {}'.format(len(source_files), len(target_files)))
        
        # List(Operation)
        ops = []
        
        def to_source(target):
            return target.replace(task['target'], task['source'])
        
        def to_target(source):
            return source.replace(task['source'], task['target'])

        #%% update file
        for source in source_files:
            target = to_target(source)
            if target in target_files:
                source_mtime = os.path.getmtime(source)
                target_mtime = os.path.getmtime(target)

                if source_mtime > target_mtime and source_mtime > record['update_time']:
                    ops.append(Op( target, 'update', source))
                elif target_mtime > source_mtime and target_mtime > record['update_time']:
                    ops.append(Op( source, 'update', target))
        
        #%% set previous file set
        previous_target_files = record[task['name']]
        previous_source_files = set()
        for target in previous_target_files:
            previous_source_files.add(to_source(target))
        
        for new_file in source_files - previous_source_files:
            ops.append(Op( to_target(new_file), 'new', new_file))
        for less_file in previous_source_files - source_files:
            ops.append(Op( to_target(less_file), 'delete'))

        for new_file in target_files - previous_target_files:
            ops.append(Op( to_source(new_file), 'new', new_file))
        for less_file in previous_target_files - target_files:
            ops.append(Op( to_source(less_file), 'delete'))

        if not args.test:
            print('Copying and deleting task{}...'.format(task['name']))
            pbar = tqdm(ops)
            for op in pbar:
                op.run()
                
        # writing log file:
        with open(logfile, 'a', encoding='UTF-8') as f:
            f.write('===== Task: {}.   Total Operation: {} =====\n'.format(task['name'], len(ops)))
            for op in ops:
                f.write('{}\n'.format(op.__str__()))
            print('Write log file in ** {} **'.format(logfile))

        # update record
        record[task['name']] = get_file_set(task['target'], task['filter'])
    
    record['update_time'] = time.time() + 3
    
    if not args.test:
        with open('record.pkl', 'wb') as f:
            pickle.dump(record, f)