import os
import fnmatch
import argparse
from tqdm import tqdm
import yaml
import shutil
import time
import datetime
from distutils.util import strtobool

update_time_file = 'last_update.txt'

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

class Op():
    def __init__(self, method, target, source=None):
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


if __name__ == '__main__':
    # args
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file", help="task setting in .yaml")
    parser.add_argument('--test', action='store_true', help="log out files but don't modify")
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

    if os.path.isfile(update_time_file):
        with open(update_time_file, 'r') as f:
            last_update_time = float(f.read())
    else:        
        last_update_time = 0.0

    # log file
    if args.test:
        logfile = 'test.log'
    else:
        logfile = os.path.join('./log', datetime.datetime.now().strftime('%Y%m%d_%H%M%S.log'))
    open(logfile, "w").close()

    for task in tasks:
        print('Backuping task {} ...'.format(task['name']))

        task['dont_delete'] = strtobool(task['dont_delete'])

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
        
        # update file
        for source in source_files:
            target = source.replace(task['source'], task['target'])
            if target in target_files:

                source_mtime = os.path.getmtime(source)
                target_mtime = os.path.getmtime(target)

                # source_update_time, target_update_time, last_update_time -> update ab , update ba , do nothing
                if source_mtime > target_mtime and source_mtime > last_update_time:
                    ops.append(Op('update', target, source))
                elif target_mtime > source_mtime and target_mtime > last_update_time:
                    ops.append(Op('update', source, target))
            # if source have but target don't have
            else:
                source_mtime = os.path.getmtime(source)
                if source_mtime > last_update_time:
                    ops.append(Op('new', target, source))
                elif not task['dont_delete']:
                    ops.append(Op('delete', source))


        # if target have but source don't have
        for target in target_files:
            source = target.replace(task['target'], task['source'])
            if not source in source_files:
                target_mtime = os.path.getmtime(target)
                
                if target_mtime > last_update_time:
                    ops.append(Op('new', source, target))
                elif not task['dont_delete']:
                    ops.append(Op('delete', target))

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

    # update lastupdate time
    if not args.test:
        with open(update_time_file, 'w') as f:
            f.write(str(time.time() + 5))
