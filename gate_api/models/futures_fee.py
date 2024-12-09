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


class FuturesFee(object):
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
    openapi_types = {'taker_fee': 'str', 'maker_fee': 'str'}

    attribute_map = {'taker_fee': 'taker_fee', 'maker_fee': 'maker_fee'}

    def __init__(self, taker_fee=None, maker_fee=None, local_vars_configuration=None):  # noqa: E501
        # type: (str, str, Configuration) -> None
        """FuturesFee - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._taker_fee = None
        self._maker_fee = None
        self.discriminator = None

        if taker_fee is not None:
            self.taker_fee = taker_fee
        if maker_fee is not None:
            self.maker_fee = maker_fee

    @property
    def taker_fee(self):
        """Gets the taker_fee of this FuturesFee.  # noqa: E501

        Taker fee  # noqa: E501

        :return: The taker_fee of this FuturesFee.  # noqa: E501
        :rtype: str
        """
        return self._taker_fee

    @taker_fee.setter
    def taker_fee(self, taker_fee):
        """Sets the taker_fee of this FuturesFee.

        Taker fee  # noqa: E501

        :param taker_fee: The taker_fee of this FuturesFee.  # noqa: E501
        :type: str
        """

        self._taker_fee = taker_fee

    @property
    def maker_fee(self):
        """Gets the maker_fee of this FuturesFee.  # noqa: E501

        maker fee  # noqa: E501

        :return: The maker_fee of this FuturesFee.  # noqa: E501
        :rtype: str
        """
        return self._maker_fee

    @maker_fee.setter
    def maker_fee(self, maker_fee):
        """Sets the maker_fee of this FuturesFee.

        maker fee  # noqa: E501

        :param maker_fee: The maker_fee of this FuturesFee.  # noqa: E501
        :type: str
        """

        self._maker_fee = maker_fee

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
        if not isinstance(other, FuturesFee):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FuturesFee):
            return True

        return self.to_dict() != other.to_dict()
