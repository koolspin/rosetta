from graph.enums import CapabilitiesType
from graph.mime_types import MimeTypes


class PadCapabilities:
    """
    Defines the capabilities of a pad. Used for restrict pads to certain formats.
    """
    def __init__(self, cap_match_type, mime_type, pad_props) -> None:
        super().__init__()
        self._cap_match_type = cap_match_type
        self.mime_type = mime_type
        self.pad_properties = pad_props

    def __str__(self) -> str:
        return 'caps: {0}, {1}'.format(self._cap_match_type, self.mime_type)

    @staticmethod
    def create_caps_any():
        """
        Creates an instance of a caps object that will match anything
        :return: A caps object
        """
        caps = PadCapabilities(CapabilitiesType.MATCH_ANY, MimeTypes.ALL, {})
        return caps

    @staticmethod
    def create_caps_none():
        """
        Creates an instance of a caps object that will match nothing
        :return: A caps object
        """
        caps = PadCapabilities(CapabilitiesType.MATCH_NONE, '', {})
        return caps

    @staticmethod
    def create_caps_normal(mime_type, pad_props):
        """
        Creates an instance of a caps object with a mime type and properties for filtering
        :param mime_type: The mime_type of the caps object - ex: application/json
        :param pad_props: Properties to further qualify the match - ex: ????
        :return: A caps object
        """
        caps = PadCapabilities(CapabilitiesType.MATCH_NORMAL, mime_type, pad_props)
        return caps

