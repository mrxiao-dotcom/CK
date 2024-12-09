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


class FlashSwapPreviewRequest(object):
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
    openapi_types = {'sell_currency': 'str', 'sell_amount': 'str', 'buy_currency': 'str', 'buy_amount': 'str'}

    attribute_map = {
        'sell_currency': 'sell_currency',
        'sell_amount': 'sell_amount',
        'buy_currency': 'buy_currency',
        'buy_amount': 'buy_amount',
    }

    def __init__(
        self, sell_currency=None, sell_amount=None, buy_currency=None, buy_amount=None, local_vars_configuration=None
    ):  # noqa: E501
        # type: (str, str, str, str, Configuration) -> None
        """FlashSwapPreviewRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._sell_currency = None
        self._sell_amount = None
        self._buy_currency = None
        self._buy_amount = None
        self.discriminator = None

        self.sell_currency = sell_currency
        if sell_amount is not None:
            self.sell_amount = sell_amount
        self.buy_currency = buy_currency
        if buy_amount is not None:
            self.buy_amount = buy_amount

    @property
    def sell_currency(self):
        """Gets the sell_currency of this FlashSwapPreviewRequest.  # noqa: E501

        The name of the asset being sold, as obtained from the \"GET /flash_swap/currency_pairs\" API, which retrieves a list of supported flash swap currency pairs.  # noqa: E501

        :return: The sell_currency of this FlashSwapPreviewRequest.  # noqa: E501
        :rtype: str
        """
        return self._sell_currency

    @sell_currency.setter
    def sell_currency(self, sell_currency):
        """Sets the sell_currency of this FlashSwapPreviewRequest.

        The name of the asset being sold, as obtained from the \"GET /flash_swap/currency_pairs\" API, which retrieves a list of supported flash swap currency pairs.  # noqa: E501

        :param sell_currency: The sell_currency of this FlashSwapPreviewRequest.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and sell_currency is None:  # noqa: E501
            raise ValueError("Invalid value for `sell_currency`, must not be `None`")  # noqa: E501

        self._sell_currency = sell_currency

    @property
    def sell_amount(self):
        """Gets the sell_amount of this FlashSwapPreviewRequest.  # noqa: E501

        Amount to sell. It is required to choose one parameter between `sell_amount` and `buy_amount`  # noqa: E501

        :return: The sell_amount of this FlashSwapPreviewRequest.  # noqa: E501
        :rtype: str
        """
        return self._sell_amount

    @sell_amount.setter
    def sell_amount(self, sell_amount):
        """Sets the sell_amount of this FlashSwapPreviewRequest.

        Amount to sell. It is required to choose one parameter between `sell_amount` and `buy_amount`  # noqa: E501

        :param sell_amount: The sell_amount of this FlashSwapPreviewRequest.  # noqa: E501
        :type: str
        """

        self._sell_amount = sell_amount

    @property
    def buy_currency(self):
        """Gets the buy_currency of this FlashSwapPreviewRequest.  # noqa: E501

        The name of the asset being purchased, as obtained from the \"GET /flash_swap/currency_pairs\" API, which provides a list of supported flash swap currency pairs.  # noqa: E501

        :return: The buy_currency of this FlashSwapPreviewRequest.  # noqa: E501
        :rtype: str
        """
        return self._buy_currency

    @buy_currency.setter
    def buy_currency(self, buy_currency):
        """Sets the buy_currency of this FlashSwapPreviewRequest.

        The name of the asset being purchased, as obtained from the \"GET /flash_swap/currency_pairs\" API, which provides a list of supported flash swap currency pairs.  # noqa: E501

        :param buy_currency: The buy_currency of this FlashSwapPreviewRequest.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and buy_currency is None:  # noqa: E501
            raise ValueError("Invalid value for `buy_currency`, must not be `None`")  # noqa: E501

        self._buy_currency = buy_currency

    @property
    def buy_amount(self):
        """Gets the buy_amount of this FlashSwapPreviewRequest.  # noqa: E501

        Amount to buy. It is required to choose one parameter between `sell_amount` and `buy_amount`  # noqa: E501

        :return: The buy_amount of this FlashSwapPreviewRequest.  # noqa: E501
        :rtype: str
        """
        return self._buy_amount

    @buy_amount.setter
    def buy_amount(self, buy_amount):
        """Sets the buy_amount of this FlashSwapPreviewRequest.

        Amount to buy. It is required to choose one parameter between `sell_amount` and `buy_amount`  # noqa: E501

        :param buy_amount: The buy_amount of this FlashSwapPreviewRequest.  # noqa: E501
        :type: str
        """

        self._buy_amount = buy_amount

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
        if not isinstance(other, FlashSwapPreviewRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FlashSwapPreviewRequest):
            return True

        return self.to_dict() != other.to_dict()
