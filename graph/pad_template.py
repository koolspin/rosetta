from graph.enums import PadDirection, PadPresence


class PadTemplate:
    """
    The template used to configure the actual pads for a filter
    """
    DEFAULT_SOURCE_NAME_TEMPLATE = 'src_{0}'
    DEFAULT_SINK_NAME_TEMPLATE = 'sink_{0}'

    def __init__(self, name_template, direction, presence, caps) -> None:
        super().__init__()
        self._name_template = name_template
        self._direction = direction
        self._presence = presence
        self._capabilities = caps

    def __str__(self) -> str:
        return 'pad-template: {0}-{1}-{2}'.format(self._name_template, self._direction, self._presence)

    @property
    def name_template(self):
        return self._name_template

    @property
    def direction(self):
        return self._direction

    @property
    def presence(self):
        return self._presence

    @property
    def caps(self):
        return self._capabilities

    def is_present_always(self):
        """
        Returns true if the presence of this pad is always present
        :return: true if the pad is always present
        """
        return self._presence == PadPresence.ALWAYS

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

    def is_direction_unknown(self):
        """
        Returns true if the pad direction is unknown
        :return: true if the pad direction is unknown
        """
        return self._direction == PadDirection.UNKNOWN

    @staticmethod
    def create_pad_always_source(caps, name_template=None):
        """
        Create a source pad that is always present.
        :param caps: An array of caps objects to be used for this pad.
        :param name_template: The name template to be used for creating new pads
        :return: A pad object
        """
        pad = None
        if name_template is None:
            pad = PadTemplate(PadTemplate.DEFAULT_SOURCE_NAME_TEMPLATE, PadDirection.SOURCE, PadPresence.ALWAYS, caps)
        else:
            pad = PadTemplate(name_template, PadDirection.SOURCE, PadPresence.ALWAYS, caps)
        return pad

    @staticmethod
    def create_pad_always_sink(caps, name_template=None):
        """
        Create a sink pad that is always present.
        :param caps: An array of caps objects to be used for this pad.
        :param name_template: The name template to be used for creating new pads
        :return: A pad object
        """
        pad = None
        if name_template is None:
            pad = PadTemplate(PadTemplate.DEFAULT_SINK_NAME_TEMPLATE, PadDirection.SINK, PadPresence.ALWAYS, caps)
        else:
            pad = PadTemplate(name_template, PadDirection.SINK, PadPresence.ALWAYS, caps)
        return pad

    @staticmethod
    def create_pad_source(presence, caps, name_template=None):
        """
        Create a source pad with the specified presence.
        :param presence: The presence of this pad.
        :param caps: An array of caps objects to be used for this pad.
        :param name_template: The name template to be used for creating new pads
        :return: A source pad object
        """
        pad = None
        if name_template is None:
            pad = PadTemplate(PadTemplate.DEFAULT_SOURCE_NAME_TEMPLATE, PadDirection.SOURCE, presence, caps)
        else:
            pad = PadTemplate(name_template, PadDirection.SOURCE, presence, caps)
        return pad

    @staticmethod
    def create_pad_sink(presence, caps, name_template=None):
        """
        Create a sink pad with the specified presence.
        :param name_template: The name template to be used for creating new pads
        :param presence: The presence of this pad.
        :param caps: An array of caps objects to be used for this pad.
        :return: A sink pad object
        """
        pad = None
        if name_template is None:
            pad = PadTemplate(PadTemplate.DEFAULT_SINK_NAME_TEMPLATE, PadDirection.SINK, presence, caps)
        else:
            pad = PadTemplate(name_template, PadDirection.SINK, presence, caps)
        return pad

