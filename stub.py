import argparse
import importlib
import inspect
import os


class Outputter:
    def __init__(self, file, options, indent_level=0):
        self.file = file
        self.options = options
        self.indent_level = indent_level

    def comment(self, comment):
        for line in comment.splitlines():
            self.line('# ' + line)

    def doc(self, doc):
        if not self.options.include_docs:
            return
        if doc is None:
            return
        self.comment(doc)

    def line(self, line):
        indent = ' ' * (self.indent_level * 4)
        self.file.write(indent + str(line) + '\n')

    def indent(self):
        return Outputter(self.file, self.options, self.indent_level + 1)

    def blank(self):
        self.line('')

    def value_hint(self, name, value):
        if not self.options.include_values:
            return
        self.comment('Note: {} had the following value:'.format(name))
        self.comment(repr(value))


def get_class_name(class_):
    return class_.__name__


def get_bases_string(class_):
    # XXX: doesn't work if a base is from another package!

    bases = class_.__bases__

    if len(bases) == 1 and bases[0] == object:
        return ''
    else:
        return '(' + ', '.join(get_class_name(base) for base in bases) + ')'


def is_inherited(class_, member):
    if not hasattr(member, '__objclass__'):
        return False

    return member.__objclass__ != class_


def stub_class(name, class_, out):
    out.doc(inspect.getdoc(class_))
    bases = get_bases_string(class_)
    out.line('class {}{}:'.format(name, bases))
    out = out.indent()

    has_member = False
    for name, member in inspect.getmembers(class_):
        if is_inherited(class_, member):
            continue

        has_member = True

        # XXX refactor; similar stuff in stub()
        if inspect.isfunction(member):
            stub_function(name, member, out)
        else:
            stub_value(name, member, out)

    if not has_member:
        out.line('pass')


def stub_function(name, func, out):
    # TODO: handle arguments properly
    out.doc(inspect.getdoc(func))
    out.line('def {}(*args, **kwargs):'.format(name))
    out = out.indent()
    out.line('pass')


def guess_value_type(value):
    # TODO: more types...
    if isinstance(value, str):
        return 'str'
    else:
        return 'any'


def stub_value(name, value, out):
    type_ = guess_value_type(value)
    out.value_hint(name, value)
    out.line('{} {}'.format(type_, name))


def get_exports(module):
    it = inspect.getmembers(module)
    if hasattr(module, '__all__'):
        all_members = set(module.__all__)
        for name, member in it:
            if name in all_members:
                yield name, member
    else:
        for name, member in it:
            if not name.startswith('_'):
                yield name, member


def is_magic(name):
    return name.startswith('__') and name.endswith('__')


def stub(module, out, options):
    # TODO: can/should we detect whether a member was defined
    # in another module? (i.e., is an import)

    if options.exports_only:
        members = get_exports(module)
    else:
        members = inspect.getmembers(module)

    for name, member in members:
        # TODO: is this the right thing to do?
        if is_magic(name):
            continue

        if name in options.hiding:
            continue

        if inspect.ismodule(member):
            out.comment('module not stubbed: ' + str(name))
        elif inspect.isclass(member):
            stub_class(name, member, out)
        elif inspect.isfunction(member):
            stub_function(name, member, out)
        elif inspect.isgeneratorfunction(member):
            out.comment('generator: ' + name)
        else:
            stub_value(name, member, out)
        # TODO: any others?

        out.blank()


def is_probably_package(mod):
    try:
        path = inspect.getsourcefile(mod)
    except TypeError:
        # implies it's a built-in module, class or function
        return False

    if path is None:
        return False
    else:
        return os.path.basename(path) == '__init__.py'


def make_parent_dirs(path):
    parent = os.path.dirname(path)
    try:
        os.makedirs(parent)
    except os.error:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('module')
    parser.add_argument('out_dir')
    parser.add_argument('--include-docs', action='store_true',
            help='include docstrings in output')
    parser.add_argument('--include-values', action='store_true',
            help='include runtime values in output')
    parser.add_argument('--exports-only', action='store_true',
            help='include only what you would get by importing *')
    parser.add_argument('--force-package', action='store_true',
            help='force output to be in an __init__.py')
    parser.add_argument('--hiding', action='append', default=[],
            help='exclude a member')
    parser.add_argument('--overwrite', action='store_true',
            help='allow overwriting an existing stub')
    args = parser.parse_args()

    try:
        mod = importlib.import_module(args.module)
    except ImportError:
        print('Module {} does not exist'.format(args.module))
        return
    except:
        print('Failed to import {}'.format(args.module))
        return

    components = args.module.split('.')
    if is_probably_package(mod) or args.force_package:
        components.append('__init__.py')
    else:
        components[-1] += '.py'
    out_path = os.path.join(args.out_dir, *components)

    make_parent_dirs(out_path)

    if os.path.exists(out_path) and not args.overwrite:
        print('Refusing to overwrite {}'.format(out_path))
        return

    with open(out_path, 'w') as out_file:
        out = Outputter(out_file, args)
        stub(mod, out, args)


if __name__ == '__main__':
    main()
