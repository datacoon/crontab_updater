import datetime
import os
import re
import subprocess
import sys

from vars import STUB


class EmptyCrontabs(Exception):
    pass


class CrontabUpdater:
    def __init__(self, prefix='crontab', dirname='crontabs', filelim=10):
        self.prefix = prefix
        self.dirname = dirname
        self.filelim = filelim
        self.timelet = None
        self.proj = None
        self.script = None
        try:
            os.makedirs(self.dirname)
        except FileExistsError:
            pass

    @staticmethod
    def get_crontabs_from_file(crontabs_filename):
        with open(crontabs_filename, 'rt') as handler:
            return [line for line in handler.readlines() if not line.startswith('#')]

    def fix_script_name(self):
        self.script = self.script.split('.')[0]

    def get_crontab_filename(self):
        return os.path.join(self.dirname, f'{self.prefix}{datetime.datetime.now():%Y%m%d%H%M%S%f}')

    def new(self):
        return STUB.format(timelet=self.timelet, proj=self.proj, script=self.script)

    def dump_from_subprocess(self):
        print("Dumping current crontabs from subprocess...")
        crontabs_filename = self.get_crontab_filename()
        try:
            subprocess_output = subprocess.check_output(['crontab', '-l'])
        except subprocess.CalledProcessError:
            raise EmptyCrontabs("There are no crontabs; aborting dump")
        with open(crontabs_filename, 'wb') as handler:
            handler.write(subprocess_output)
        print(f"Dumped to {crontabs_filename}")
        return crontabs_filename

    def dump_from_var(self, crontabs):
        print("Dumping current crontabs from variable...")
        crontabs_filename = self.get_crontab_filename()
        crontabs.sort()
        with open(crontabs_filename, 'wt') as handler:
            handler.write(''.join(crontabs))
        os.system(f"crontab {crontabs_filename}")
        print(f"...dumped to {crontabs_filename}")
        self.del_redundant_files()

    def restore(self):
        print('Restoring...')
        dir_contents = os.listdir(self.dirname)
        if not dir_contents:
            raise RuntimeError(f"There are no backups in {self.dirname}; aborting restore")
        most_recent_filename = os.path.join(self.dirname, max(dir_contents))
        print(f"...from {most_recent_filename}...")
        most_recent_crontabs = self.get_crontabs_from_file(most_recent_filename)
        print(f"Found {len(most_recent_crontabs)} crontabs")
        self.dump_from_var(most_recent_crontabs)
        print("...done restoring")

    def add(self):
        print('Adding...')
        try:
            crontabs_filename = self.dump_from_subprocess()
        except EmptyCrontabs as e:
            print(e)
            crontabs_filename = None
            curr_crontabs = set()
        else:
            curr_crontabs = set(self.get_crontabs_from_file(crontabs_filename))
        prev_len = len(curr_crontabs)
        curr_crontabs.add(self.new())
        if crontabs_filename and len(curr_crontabs) == prev_len:
            os.remove(crontabs_filename)
            raise RuntimeError("New tab is already there")
        self.dump_from_var(list(curr_crontabs))
        print("...done adding")

    def delete(self):
        print('Deleting...')
        crontabs_filename = self.dump_from_subprocess()
        curr_crontabs = self.get_crontabs_from_file(crontabs_filename)
        for indx in range(len(curr_crontabs)):
            if f"/{self.proj}/{self.script}.py >" in curr_crontabs[indx]:
                if self.timelet and self.timelet not in curr_crontabs[indx]:
                    continue
                del curr_crontabs[indx]
                self.dump_from_var(curr_crontabs)
                print("...done deleting")
                break
        else:
            os.remove(crontabs_filename)
            raise RuntimeError(f"{self.proj}/{self.script} is not there! Deleted {crontabs_filename}")

    def sort(self):
        print('Sorting...')
        self.dump_from_var(self.get_crontabs_from_file(self.dump_from_subprocess()))
        print("...done sorting")

    def del_redundant_files(self):
        print("Deleting redundant files...")
        pattern = re.compile(self.prefix + r'\d+')
        prev_crontabs = sorted(filter(pattern.match, os.listdir(self.dirname)))
        outdated = len(prev_crontabs) - self.filelim
        if outdated > 0:
            print(f"Removing {outdated} files...")
            for index in range(outdated):
                os.remove(os.path.join(self.dirname, prev_crontabs[index]))
            print("...done deleting redundant files")
        else:
            print("Nothing to remove")

    def launch(self):
        argv = sys.argv
        if len(argv) == 5:
            _, command, self.timelet, self.proj, self.script = argv
            self.fix_script_name()
            if command == 'del':  # delete with timelet provided
                self.delete()
            elif command == 'add':  # add from sys.argv
                self.add()
            else:
                raise RuntimeError(f"Odd command {command}!")
        elif len(argv) == 4:
            _, command, self.proj, self.script = argv
            self.fix_script_name()
            if command == 'del':  # delete without timelet provided
                self.delete()
            else:
                raise RuntimeError(f"Odd command {command}!")
        elif len(argv) == 2:
            command = argv[1]  # dump | sort
            if command == 'restore':
                self.restore()
            elif command == 'dump':
                self.dump_from_subprocess()
            elif command == 'sort':
                self.sort()
            else:
                raise RuntimeError(f"Odd command '{command}'!")
        elif len(argv) == 1:  # help
            crontab_template = '"0 9 * * *" dirname script'
            print("For restoring crontabs from most recent file, use 'python crontab_updater.py restore'")
            print(f"For adding a crontab, use 'python crontab_updater.py add {crontab_template}'")
            print(f"For deleting a crontab, use 'python crontab_updater.py del dirname script' "
                  f"or 'python crontab_updater.py del {crontab_template}'")
            print("For dumping current crontabs to file, use 'python crontab_updater.py dump'")
            print("For sorting current crontabs, use 'python crontab_updater.py sort'")
        else:
            raise RuntimeError(f"Something funny this way comes: {argv}!")


if __name__ == '__main__':
    CrontabUpdater().launch()
