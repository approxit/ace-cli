from ace.commands.base import BaseCommand
from ace.utils import load_config


class Command(BaseCommand):
    help = 'show config'

    def handle(self, **kwargs):
        config = load_config()

        for i, section in enumerate(config.sections()):
            print('{}[{}]'.format('\n' if i else '', section))

            for key, value in config.items(section):
                print('  {} = {}'.format(key, value))
