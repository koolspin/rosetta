from graph.enums import PadDirection


class Pad:
    """
    Pad object - used to transfer data between elements
    """
    def __init__(self, pad_template=None, name=None) -> None:
        super().__init__()
        if name is None:
            # TODO: Handle corner cases here and also ensure the name is actually unique
            if pad_template is not None:
                self._name = pad_template.name_template().format(42)
            else:
                self._name = 'Unknown'
        else:
            self._name = name
        if pad_template is None:
            self._template = None
            self._direction = PadDirection.UNKNOWN
            self._capabilities = None
        else:
            self._template = pad_template
            self._direction = pad_template.direction
            self._capabilities = pad_template.caps

    @property
    def name(self):
        return self._name

    @property
    def direction(self):
        return self._direction

    @property
    def caps(self):
        return self._capabilities

    @staticmethod
    def create_pad_from_template(pad_template, name=None):
        """
        Creates a new pad based on the given template
        :param pad_template: The template on which to base this pad
        :param name: The name of this pad. If none, then an unique name will be generated
        :return: A new Pad instance
        """
        new_pad = Pad(pad_template, name)
        return new_pad

    def is_src(self):
        """
        Returns true if this is a src pad
        :return: true if this is a src pad
        """
        return self._direction == PadDirection.SOURCE

    def is_sink(self):
        """
        Returns true if this is a sink pad
        :return: true if this is a sink pad
        """
        return self._direction == PadDirection.SINK

