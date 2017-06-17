class BaseCommand():
    """Base class for CLI commands."""
    help = None

    def add_parser(self, name, subparsers):
        """Gives hook to add subparser into root command line parser.

        Args:
            subparsers (argparse._SubParsersAction): Command line parser to hook into.

        """
        kwargs = {}

        if self.help is not None:
            kwargs['help'] = self.help

        parser = subparsers.add_parser(name, **kwargs)

        self.add_arguments(parser)

    def add_arguments(self, parser):
        """Gives hook to add arguments into command line parser.

        Args:
            parser (argparse.ArgumentParser): Current command line parser to hook into.

        """
        pass

    def handle(self, **kwargs):
        """Runs the actual command.

        Args:
            **kwargs: Keyword arguments for command.

        """
        raise NotImplementedError('{} must implement handle() method!'.format(self.__class__.__name__))
