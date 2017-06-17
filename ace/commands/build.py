import os
from collections import OrderedDict
from itertools import chain
from pathlib import Path
from subprocess import run, CalledProcessError

from ace.commands.base import BaseCommand
from ace.utils import load_config, print_flush


class Command(BaseCommand):
    """Build the code
    
    Attributes:
        config (configparser.ConfigParser): 
    
    """
    help = 'compile source files based on config'

    def __init__(self):
        self.config = None

    def add_arguments(self, parser):
        parser.add_argument('targets', nargs='*', metavar='target', help='selective target to build')
        parser.add_argument('-f', '--force', action='store_true', help='build without cache')

    def handle(self, targets, force, **kwargs):
        self.config = load_config()
        self.file_extensions = self.config.get('build', 'file_extensions').split()
        self.build_directory = Path(self.config.get('dirs', 'tmp'))
        self.lib_directory = Path(self.config.get('dirs', 'lib'))
        self.bin_directory = Path(self.config.get('dirs', 'bin'))
        self.force_build = force

        self.build_targets(targets)

    def build_targets(self, targets):
        targets_config = self.get_targets_config() or self.get_default_targets_config()

        if not targets:
            targets = targets_config.keys()

        for target in targets:
            if target not in targets_config:
                raise ValueError('Target "{}" not found in config files!'.format(target))

            target_config = targets_config[target]
            build_method_name = 'build_{}_type'.format(target_config.get('type', 'exec'))

            try:
                build_method = getattr(self, build_method_name)
            except AttributeError:
                raise ValueError('Target "{}" has unknown type ""!'.format(target, target_config['type']))

            build_method(target, Path(target_config['source']))

    def get_targets_config(self):
        return OrderedDict(
            (s.split('.', 1)[-1], self.config[s]) for s in self.config.sections() if s.startswith('build.')
        )

    def get_default_targets_config(self):
        return OrderedDict([
            (Path('.').resolve().name, {
                'source': Path('src'),
            })
        ])

    def build_static_type(self, target, directory):
        print_flush('Building {} target...'.format(target))

        build_files = self.build_files(target, directory)

        print_flush('Linking static library {}... '.format(target), end='')

        lib_file = self.lib_directory / '{}.lib'.format(target)
        self.prepare_file_dir(lib_file)

        with open(lib_file, 'wb') as target_file:
            for build_file in build_files:
                with open(build_file, 'rb') as f:
                    while True:
                        data = f.read(1024 * 1024)

                        if data:
                            target_file.write(data)
                        else:
                            break

        print_flush('done')

        print_flush('Building {} target done'.format(target))

    def build_exec_type(self, target, directory):
        print_flush('Building {} target...'.format(target))

        build_files = self.build_files(target, directory)

        print_flush('Linking executable {}... '.format(target), end='')

        bin_file = self.bin_directory / target
        self.prepare_file_dir(bin_file)

        build_command = '{} {} -o {} {}'.format(
            self.config.get('build', 'exec'),
            self.config.get('build', 'link_flags'),
            bin_file,
            ' '.join(str(f) for f in build_files)
        )
        build_command = os.path.expandvars(build_command)

        try:
            run(build_command, check=True)
        except CalledProcessError as e:
            exit(e.returncode)

        print_flush('done')

        print_flush('Building {} target done'.format(target))

    def build_files(self, target, directory):
        build_files = []
        for source_file in self.find_source_files(directory):
            build_file = self.get_build_file(target, directory, source_file)
            self.prepare_file_dir(build_file)
            self.build_file(directory, source_file, build_file)
            build_files.append(build_file)

        return build_files

    def find_source_files(self, directory):
        return chain.from_iterable(directory.rglob(f'*{ext}') for ext in self.file_extensions)

    def get_build_file(self, target, directory, source_file):
        return self.build_directory / target / source_file.relative_to(directory).with_suffix('.o')

    def prepare_file_dir(self, build_file):
        build_file.parent.mkdir(parents=True, exist_ok=True)

    def build_file(self, directory, source_file, build_file):
        print_flush('Building {}... '.format(source_file.relative_to(directory)), end='')

        if not self.force_build and self.is_cache_valid(source_file, build_file):
            print_flush('cached')
            return

        build_command = '{} {} -o {} {}'.format(
            self.config.get('build', 'exec'),
            self.config.get('build', 'compile_flags'),
            build_file.absolute(),
            source_file.relative_to(directory)
        )
        build_command = os.path.expandvars(build_command)

        try:
            run(build_command, check=True, cwd=str(directory))
        except CalledProcessError as e:
            exit(e.returncode)

        print_flush('done')

    def is_cache_valid(self, source_file, build_file):
        try:
            source_mtime = os.path.getmtime(source_file)
            build_mtime = os.path.getmtime(build_file)
        except OSError:
            return False

        return source_mtime < build_mtime
