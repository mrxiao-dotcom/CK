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


class TriggerTime(object):
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
    openapi_types = {'trigger_time': 'int'}

    attribute_map = {'trigger_time': 'triggerTime'}

    def __init__(self, trigger_time=None, local_vars_configuration=None):  # noqa: E501
        # type: (int, Configuration) -> None
        """TriggerTime - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._trigger_time = None
        self.discriminator = None

        if trigger_time is not None:
            self.trigger_time = trigger_time

    @property
    def trigger_time(self):
        """Gets the trigger_time of this TriggerTime.  # noqa: E501

        Timestamp of the end of the countdown, in milliseconds  # noqa: E501

        :return: The trigger_time of this TriggerTime.  # noqa: E501
        :rtype: int
        """
        return self._trigger_time

    @trigger_time.setter
    def trigger_time(self, trigger_time):
        """Sets the trigger_time of this TriggerTime.

        Timestamp of the end of the countdown, in milliseconds  # noqa: E501

        :param trigger_time: The trigger_time of this TriggerTime.  # noqa: E501
        :type: int
        """

        self._trigger_time = trigger_time

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
        if not isinstance(other, TriggerTime):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TriggerTime):
            return True

        return self.to_dict() != other.to_dict()
