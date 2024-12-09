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


class OptionsPosition(object):
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
        'user': 'int',
        'underlying': 'str',
        'underlying_price': 'str',
        'contract': 'str',
        'size': 'int',
        'entry_price': 'str',
        'mark_price': 'str',
        'mark_iv': 'str',
        'realised_pnl': 'str',
        'unrealised_pnl': 'str',
        'pending_orders': 'int',
        'close_order': 'OptionsPositionCloseOrder',
        'delta': 'str',
        'gamma': 'str',
        'vega': 'str',
        'theta': 'str',
    }

    attribute_map = {
        'user': 'user',
        'underlying': 'underlying',
        'underlying_price': 'underlying_price',
        'contract': 'contract',
        'size': 'size',
        'entry_price': 'entry_price',
        'mark_price': 'mark_price',
        'mark_iv': 'mark_iv',
        'realised_pnl': 'realised_pnl',
        'unrealised_pnl': 'unrealised_pnl',
        'pending_orders': 'pending_orders',
        'close_order': 'close_order',
        'delta': 'delta',
        'gamma': 'gamma',
        'vega': 'vega',
        'theta': 'theta',
    }

    def __init__(
        self,
        user=None,
        underlying=None,
        underlying_price=None,
        contract=None,
        size=None,
        entry_price=None,
        mark_price=None,
        mark_iv=None,
        realised_pnl=None,
        unrealised_pnl=None,
        pending_orders=None,
        close_order=None,
        delta=None,
        gamma=None,
        vega=None,
        theta=None,
        local_vars_configuration=None,
    ):  # noqa: E501
        # type: (int, str, str, str, int, str, str, str, str, str, int, OptionsPositionCloseOrder, str, str, str, str, Configuration) -> None
        """OptionsPosition - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._user = None
        self._underlying = None
        self._underlying_price = None
        self._contract = None
        self._size = None
        self._entry_price = None
        self._mark_price = None
        self._mark_iv = None
        self._realised_pnl = None
        self._unrealised_pnl = None
        self._pending_orders = None
        self._close_order = None
        self._delta = None
        self._gamma = None
        self._vega = None
        self._theta = None
        self.discriminator = None

        if user is not None:
            self.user = user
        if underlying is not None:
            self.underlying = underlying
        if underlying_price is not None:
            self.underlying_price = underlying_price
        if contract is not None:
            self.contract = contract
        if size is not None:
            self.size = size
        if entry_price is not None:
            self.entry_price = entry_price
        if mark_price is not None:
            self.mark_price = mark_price
        if mark_iv is not None:
            self.mark_iv = mark_iv
        if realised_pnl is not None:
            self.realised_pnl = realised_pnl
        if unrealised_pnl is not None:
            self.unrealised_pnl = unrealised_pnl
        if pending_orders is not None:
            self.pending_orders = pending_orders
        self.close_order = close_order
        if delta is not None:
            self.delta = delta
        if gamma is not None:
            self.gamma = gamma
        if vega is not None:
            self.vega = vega
        if theta is not None:
            self.theta = theta

    @property
    def user(self):
        """Gets the user of this OptionsPosition.  # noqa: E501

        User ID  # noqa: E501

        :return: The user of this OptionsPosition.  # noqa: E501
        :rtype: int
        """
        return self._user

    @user.setter
    def user(self, user):
        """Sets the user of this OptionsPosition.

        User ID  # noqa: E501

        :param user: The user of this OptionsPosition.  # noqa: E501
        :type: int
        """

        self._user = user

    @property
    def underlying(self):
        """Gets the underlying of this OptionsPosition.  # noqa: E501

        Underlying  # noqa: E501

        :return: The underlying of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._underlying

    @underlying.setter
    def underlying(self, underlying):
        """Sets the underlying of this OptionsPosition.

        Underlying  # noqa: E501

        :param underlying: The underlying of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._underlying = underlying

    @property
    def underlying_price(self):
        """Gets the underlying_price of this OptionsPosition.  # noqa: E501

        Underlying price (quote currency)  # noqa: E501

        :return: The underlying_price of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._underlying_price

    @underlying_price.setter
    def underlying_price(self, underlying_price):
        """Sets the underlying_price of this OptionsPosition.

        Underlying price (quote currency)  # noqa: E501

        :param underlying_price: The underlying_price of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._underlying_price = underlying_price

    @property
    def contract(self):
        """Gets the contract of this OptionsPosition.  # noqa: E501

        Options contract name  # noqa: E501

        :return: The contract of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._contract

    @contract.setter
    def contract(self, contract):
        """Sets the contract of this OptionsPosition.

        Options contract name  # noqa: E501

        :param contract: The contract of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._contract = contract

    @property
    def size(self):
        """Gets the size of this OptionsPosition.  # noqa: E501

        Position size (contract size)  # noqa: E501

        :return: The size of this OptionsPosition.  # noqa: E501
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size):
        """Sets the size of this OptionsPosition.

        Position size (contract size)  # noqa: E501

        :param size: The size of this OptionsPosition.  # noqa: E501
        :type: int
        """

        self._size = size

    @property
    def entry_price(self):
        """Gets the entry_price of this OptionsPosition.  # noqa: E501

        Entry size (quote currency)  # noqa: E501

        :return: The entry_price of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._entry_price

    @entry_price.setter
    def entry_price(self, entry_price):
        """Sets the entry_price of this OptionsPosition.

        Entry size (quote currency)  # noqa: E501

        :param entry_price: The entry_price of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._entry_price = entry_price

    @property
    def mark_price(self):
        """Gets the mark_price of this OptionsPosition.  # noqa: E501

        Current mark price (quote currency)  # noqa: E501

        :return: The mark_price of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._mark_price

    @mark_price.setter
    def mark_price(self, mark_price):
        """Sets the mark_price of this OptionsPosition.

        Current mark price (quote currency)  # noqa: E501

        :param mark_price: The mark_price of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._mark_price = mark_price

    @property
    def mark_iv(self):
        """Gets the mark_iv of this OptionsPosition.  # noqa: E501

        Implied volatility  # noqa: E501

        :return: The mark_iv of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._mark_iv

    @mark_iv.setter
    def mark_iv(self, mark_iv):
        """Sets the mark_iv of this OptionsPosition.

        Implied volatility  # noqa: E501

        :param mark_iv: The mark_iv of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._mark_iv = mark_iv

    @property
    def realised_pnl(self):
        """Gets the realised_pnl of this OptionsPosition.  # noqa: E501

        Realized PNL  # noqa: E501

        :return: The realised_pnl of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._realised_pnl

    @realised_pnl.setter
    def realised_pnl(self, realised_pnl):
        """Sets the realised_pnl of this OptionsPosition.

        Realized PNL  # noqa: E501

        :param realised_pnl: The realised_pnl of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._realised_pnl = realised_pnl

    @property
    def unrealised_pnl(self):
        """Gets the unrealised_pnl of this OptionsPosition.  # noqa: E501

        Unrealized PNL  # noqa: E501

        :return: The unrealised_pnl of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._unrealised_pnl

    @unrealised_pnl.setter
    def unrealised_pnl(self, unrealised_pnl):
        """Sets the unrealised_pnl of this OptionsPosition.

        Unrealized PNL  # noqa: E501

        :param unrealised_pnl: The unrealised_pnl of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._unrealised_pnl = unrealised_pnl

    @property
    def pending_orders(self):
        """Gets the pending_orders of this OptionsPosition.  # noqa: E501

        Current open orders  # noqa: E501

        :return: The pending_orders of this OptionsPosition.  # noqa: E501
        :rtype: int
        """
        return self._pending_orders

    @pending_orders.setter
    def pending_orders(self, pending_orders):
        """Sets the pending_orders of this OptionsPosition.

        Current open orders  # noqa: E501

        :param pending_orders: The pending_orders of this OptionsPosition.  # noqa: E501
        :type: int
        """

        self._pending_orders = pending_orders

    @property
    def close_order(self):
        """Gets the close_order of this OptionsPosition.  # noqa: E501


        :return: The close_order of this OptionsPosition.  # noqa: E501
        :rtype: OptionsPositionCloseOrder
        """
        return self._close_order

    @close_order.setter
    def close_order(self, close_order):
        """Sets the close_order of this OptionsPosition.


        :param close_order: The close_order of this OptionsPosition.  # noqa: E501
        :type: OptionsPositionCloseOrder
        """

        self._close_order = close_order

    @property
    def delta(self):
        """Gets the delta of this OptionsPosition.  # noqa: E501

        Delta  # noqa: E501

        :return: The delta of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._delta

    @delta.setter
    def delta(self, delta):
        """Sets the delta of this OptionsPosition.

        Delta  # noqa: E501

        :param delta: The delta of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._delta = delta

    @property
    def gamma(self):
        """Gets the gamma of this OptionsPosition.  # noqa: E501

        Gamma  # noqa: E501

        :return: The gamma of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._gamma

    @gamma.setter
    def gamma(self, gamma):
        """Sets the gamma of this OptionsPosition.

        Gamma  # noqa: E501

        :param gamma: The gamma of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._gamma = gamma

    @property
    def vega(self):
        """Gets the vega of this OptionsPosition.  # noqa: E501

        Vega  # noqa: E501

        :return: The vega of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._vega

    @vega.setter
    def vega(self, vega):
        """Sets the vega of this OptionsPosition.

        Vega  # noqa: E501

        :param vega: The vega of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._vega = vega

    @property
    def theta(self):
        """Gets the theta of this OptionsPosition.  # noqa: E501

        Theta  # noqa: E501

        :return: The theta of this OptionsPosition.  # noqa: E501
        :rtype: str
        """
        return self._theta

    @theta.setter
    def theta(self, theta):
        """Sets the theta of this OptionsPosition.

        Theta  # noqa: E501

        :param theta: The theta of this OptionsPosition.  # noqa: E501
        :type: str
        """

        self._theta = theta

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
        if not isinstance(other, OptionsPosition):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, OptionsPosition):
            return True

        return self.to_dict() != other.to_dict()
