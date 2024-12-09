# coding: utf-8

"""
    Gate API v4

    Welcome to Gate.io API  APIv4 provides spot, margin and futures trading operations. There are public APIs to retrieve the real-time market statistics, and private APIs which needs authentication to trade on user's behalf.  # noqa: E501

    Contact: support@mail.gate.io
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from gate_api.configuration import Configuration


class UnifiedMode(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {'mode': 'str', 'enabled': 'bool'}

    attribute_map = {'mode': 'mode', 'enabled': 'enabled'}

    def __init__(self, mode=None, enabled=None, local_vars_configuration=None):  # noqa: E501
        # type: (str, bool, Configuration) -> None
        """UnifiedMode - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._mode = None
        self._enabled = None
        self.discriminator = None

        self.mode = mode
        self.enabled = enabled

    @property
    def mode(self):
        """Gets the mode of this UnifiedMode.  # noqa: E501

        Portfolio mode - cross_margin : cross margin - usdt_futures : usdt futures  # noqa: E501

        :return: The mode of this UnifiedMode.  # noqa: E501
        :rtype: str
        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Sets the mode of this UnifiedMode.

        Portfolio mode - cross_margin : cross margin - usdt_futures : usdt futures  # noqa: E501

        :param mode: The mode of this UnifiedMode.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and mode is None:  # noqa: E501
            raise ValueError("Invalid value for `mode`, must not be `None`")  # noqa: E501

        self._mode = mode

    @property
    def enabled(self):
        """Gets the enabled of this UnifiedMode.  # noqa: E501

        Is it enabled?  # noqa: E501

        :return: The enabled of this UnifiedMode.  # noqa: E501
        :rtype: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """Sets the enabled of this UnifiedMode.

        Is it enabled?  # noqa: E501

        :param enabled: The enabled of this UnifiedMode.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and enabled is None:  # noqa: E501
            raise ValueError("Invalid value for `enabled`, must not be `None`")  # noqa: E501

        self._enabled = enabled

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(
                        lambda item: (item[0], item[1].to_dict()) if hasattr(item[1], "to_dict") else item,
                        value.items(),
                    )
                )
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, UnifiedMode):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UnifiedMode):
            return True

        return self.to_dict() != other.to_dict()
