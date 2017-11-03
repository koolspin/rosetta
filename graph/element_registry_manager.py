import fnmatch
import importlib
import inspect
import os

from graph.filter_base import FilterBase


class ElementRegistryManager:
    """
    Manages a registry of elements.
    This class will iterate through the default elements location (usually specified by the ROSETTA_ELEMENTS
    environment variable. It will collect metadata for each element found to build the registry.
    Commands such as inspect.py will scan this registry to find elements to query.
    """
    BASE_CLASS_MODULE = 'graph.filter_base'
    BASE_CLASS_NAME = 'FilterBase'
    ELEMENT_MODULE_PATH = 'elements'

    def __init__(self) -> None:
        super().__init__()
        # Element files, keyed by filename. Value contains a list of fully qualified names
        self._element_files = {}
        # Element classes, keyed by fully qualified name, ex: com.urbtek.logger_sink
        # Value contains the static klass which can be used to create an instance
        self._element_classes = {}
        # TODO: Need to append other directories to this
        self._module_directories = ['./elements']

    def build_registry(self):
        """
        Build a registry of files and classes that contain elements (and perhaps other components one day)
        :return: None
        """
        for dir in self._module_directories:
            for file in os.listdir(dir):
                if fnmatch.fnmatch(file, '*.py'):
                    element_list = []
                    full_path = ElementRegistryManager.ELEMENT_MODULE_PATH + '.' + file[:-3]
                    mod = importlib.import_module(full_path)
                    # Find all of the classes within this module
                    for name, obj in inspect.getmembers(mod, inspect.isclass):
                        # This is a class, let's see if it derives from FilterBase
                        klass = getattr(mod, name)
                        for base in klass.__bases__:
                            if inspect.isclass(base):
                                if base.__module__ == ElementRegistryManager.BASE_CLASS_MODULE and base.__name__ == ElementRegistryManager.BASE_CLASS_NAME:
                                    print('{0} is an element!'.format(klass.__name__))
                                    meta = klass.get_filter_metadata()
                                    fq_name = meta[FilterBase.FILTER_META_FULLY_QUALIFIED]
                                    print('fq name: {0}'.format(fq_name))
                                    self._element_classes[fq_name] = klass
                                    element_list.append(fq_name)
                    if len(element_list) > 0:
                        # The file contains at least one element
                        self._element_files[full_path] = element_list

    def dump_registry(self):
        """
        Dump the contents of the registry by iterating through each file and each element
        :return: None
        """
        print('Dumping files within elements folder')
        for k, v in self._element_files.items():
            print('{0}'.format(k))
            for element_name in v:
                print('..{0}'.format(element_name))
        print('=================================')
        for k1, v1 in self._element_classes.items():
            print('{0}'.format(k1))
            meta = v1.get_filter_metadata()
            print('.. Rank:    {0}'.format(meta[FilterBase.FILTER_META_RANK]))
            print('.. Version: {0}'.format(meta[FilterBase.FILTER_META_VER]))
            print('.. Desc:    {0}'.format(meta[FilterBase.FILTER_META_DESC]))
            filt = v1.get_filter_pad_templates()
            for k2, v2 in filt.items():
                print('.... Pad: {0}'.format(k2))
                print('...... Name template: {0}'.format(v2.name_template))
                print('...... Direction: {0}'.format(v2.direction))
                print('...... Presence: {0}'.format(v2.presence))
                print('...... Caps:')
                caps = v2.caps
                for cap in caps:
                    print('........ {0}:'.format(str(cap)))

