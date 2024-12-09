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


class CrossMarginCurrency(object):
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
    openapi_types = {
        'name': 'str',
        'rate': 'str',
        'prec': 'str',
        'discount': 'str',
        'min_borrow_amount': 'str',
        'user_max_borrow_amount': 'str',
        'total_max_borrow_amount': 'str',
        'price': 'str',
        'loanable': 'bool',
        'status': 'int',
    }

    attribute_map = {
        'name': 'name',
        'rate': 'rate',
        'prec': 'prec',
        'discount': 'discount',
        'min_borrow_amount': 'min_borrow_amount',
        'user_max_borrow_amount': 'user_max_borrow_amount',
        'total_max_borrow_amount': 'total_max_borrow_amount',
        'price': 'price',
        'loanable': 'loanable',
        'status': 'status',
    }

    def __init__(
        self,
        name=None,
        rate=None,
        prec=None,
        discount=None,
        min_borrow_amount=None,
        user_max_borrow_amount=None,
        total_max_borrow_amount=None,
        price=None,
        loanable=None,
        status=None,
        local_vars_configuration=None,
    ):  # noqa: E501
        # type: (str, str, str, str, str, str, str, str, bool, int, Configuration) -> None
        """CrossMarginCurrency - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._rate = None
        self._prec = None
        self._discount = None
        self._min_borrow_amount = None
        self._user_max_borrow_amount = None
        self._total_max_borrow_amount = None
        self._price = None
        self._loanable = None
        self._status = None
        self.discriminator = None

        if name is not None:
            self.name = name
        if rate is not None:
            self.rate = rate
        if prec is not None:
            self.prec = prec
        if discount is not None:
            self.discount = discount
        if min_borrow_amount is not None:
            self.min_borrow_amount = min_borrow_amount
        if user_max_borrow_amount is not None:
            self.user_max_borrow_amount = user_max_borrow_amount
        if total_max_borrow_amount is not None:
            self.total_max_borrow_amount = total_max_borrow_amount
        if price is not None:
            self.price = price
        if loanable is not None:
            self.loanable = loanable
        if status is not None:
            self.status = status

    @property
    def name(self):
        """Gets the name of this CrossMarginCurrency.  # noqa: E501

        Currency name  # noqa: E501

        :return: The name of this CrossMarginCurrency.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CrossMarginCurrency.

        Currency name  # noqa: E501

        :param name: The name of this CrossMarginCurrency.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def rate(self):
        """Gets the rate of this CrossMarginCurrency.  # noqa: E501

        Minimum lending rate (hourly rate)  # noqa: E501

        :return: The rate of this CrossMarginCurrency.  # noqa: E501
        :rtype: str
        """
        return self._rate

    @rate.setter
    def rate(self, rate):
        """Sets the rate of this CrossMarginCurrency.

        Minimum lending rate (hourly rate)  # noqa: E501

        :param rate: The rate of this CrossMarginCurrency.  # noqa: E501
        :type: str
        """

        self._rate = rate

    @property
    def prec(self):
        """Gets the prec of this CrossMarginCurrency.  # noqa: E501

        Currency precision  # noqa: E501

        :return: The prec of this CrossMarginCurrency.  # noqa: E501
        :rtype: str
        """
        return self._prec

    @prec.setter
    def prec(self, prec):
        """Sets the prec of this CrossMarginCurrency.

        Currency precision  # noqa: E501

        :param prec: The prec of this CrossMarginCurrency.  # noqa: E501
        :type: str
        """

        self._prec = prec

    @property
    def discount(self):
        """Gets the discount of this CrossMarginCurrency.  # noqa: E501

        Currency value discount, which is used in total value calculation  # noqa: E501

        :return: The discount of this CrossMarginCurrency.  # noqa: E501
        :rtype: str
        """
        return self._discount

    @discount.setter
    def discount(self, discount):
        """Sets the discount of this CrossMarginCurrency.

        Currency value discount, which is used in total value calculation  # noqa: E501

        :param discount: The discount of this CrossMarginCurrency.  # noqa: E501
        :type: str
        """

        self._discount = discount

    @property
    def min_borrow_amount(self):
        """Gets the min_borrow_amount of this CrossMarginCurrency.  # noqa: E501

        Minimum currency borrow amount. Unit is currency itself  # noqa: E501

        :return: The min_borrow_amount of this CrossMarginCurrency.  # noqa: E501
        :rtype: str
        """
        return self._min_borrow_amount

    @min_borrow_amount.setter
    def min_borrow_amount(self, min_borrow_amount):
        """Sets the min_borrow_amount of this CrossMarginCurrency.

        Minimum currency borrow amount. Unit is currency itself  # noqa: E501

        :param min_borrow_amount: The min_borrow_amount of this CrossMarginCurrency.  # noqa: E501
        :type: str
        """

        self._min_borrow_amount = min_borrow_amount

    @property
    def user_max_borrow_amount(self):
        """Gets the user_max_borrow_amount of this CrossMarginCurrency.  # noqa: E501

        Maximum borrow value allowed per user, in USDT  # noqa: E501

        :return: The user_max_borrow_amount of this CrossMarginCurrency.  # noqa: E501
        :rtype: str
        """
        return self._user_max_borrow_amount

    @user_max_borrow_amount.setter
    def user_max_borrow_amount(self, user_max_borrow_amount):
        """Sets the user_max_borrow_amount of this CrossMarginCurrency.

        Maximum borrow value allowed per user, in USDT  # noqa: E501

        :param user_max_borrow_amount: The user_max_borrow_amount of this CrossMarginCurrency.  # noqa: E501
        :type: str
        """

        self._user_max_borrow_amount = user_max_borrow_amount

    @property
    def total_max_borrow_amount(self):
        """Gets the total_max_borrow_amount of this CrossMarginCurrency.  # noqa: E501

        Maximum borrow value allowed for this currency, in USDT  # noqa: E501

        :return: The total_max_borrow_amount of this CrossMarginCurrency.  # noqa: E501
        :rtype: str
        """
        return self._total_max_borrow_amount

    @total_max_borrow_amount.setter
    def total_max_borrow_amount(self, total_max_borrow_amount):
        """Sets the total_max_borrow_amount of this CrossMarginCurrency.

        Maximum borrow value allowed for this currency, in USDT  # noqa: E501

        :param total_max_borrow_amount: The total_max_borrow_amount of this CrossMarginCurrency.  # noqa: E501
        :type: str
        """

        self._total_max_borrow_amount = total_max_borrow_amount

    @property
    def price(self):
        """Gets the price of this CrossMarginCurrency.  # noqa: E501

        Price change between this currency and USDT  # noqa: E501

        :return: The price of this CrossMarginCurrency.  # noqa: E501
        :rtype: str
        """
        return self._price

    @price.setter
    def price(self, price):
        """Sets the price of this CrossMarginCurrency.

        Price change between this currency and USDT  # noqa: E501

        :param price: The price of this CrossMarginCurrency.  # noqa: E501
        :type: str
        """

        self._price = price

    @property
    def loanable(self):
        """Gets the loanable of this CrossMarginCurrency.  # noqa: E501

        Whether currency is borrowed  # noqa: E501

        :return: The loanable of this CrossMarginCurrency.  # noqa: E501
        :rtype: bool
        """
        return self._loanable

    @loanable.setter
    def loanable(self, loanable):
        """Sets the loanable of this CrossMarginCurrency.

        Whether currency is borrowed  # noqa: E501

        :param loanable: The loanable of this CrossMarginCurrency.  # noqa: E501
        :type: bool
        """

        self._loanable = loanable

    @property
    def status(self):
        """Gets the status of this CrossMarginCurrency.  # noqa: E501

        status  - `0` : disable  - `1` : enable  # noqa: E501

        :return: The status of this CrossMarginCurrency.  # noqa: E501
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this CrossMarginCurrency.

        status  - `0` : disable  - `1` : enable  # noqa: E501

        :param status: The status of this CrossMarginCurrency.  # noqa: E501
        :type: int
        """

        self._status = status

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
        if not isinstance(other, CrossMarginCurrency):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CrossMarginCurrency):
            return True

        return self.to_dict() != other.to_dict()
