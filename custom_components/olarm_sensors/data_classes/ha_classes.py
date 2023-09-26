"""
Module containing the classes for storing data between Home Assistant and the API.
Also mimics service schemas.
"""


class BypassZone:
    """
    DOCSTRING: Representation of the area number for calling the bypass service / function.
    """

    zone: int = 0

    def __init__(self, zone: int) -> None:
        self.zone = zone
        return None

    @property
    def data(self):
        """
        DOCSTRING: Returns the zone number in a dictionary for using the same function for service and switch bypassing.
        """
        return {"zone_num": self.zone}
