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


class FuturesAccount(object):
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
        'total': 'str',
        'unrealised_pnl': 'str',
        'position_margin': 'str',
        'order_margin': 'str',
        'available': 'str',
        'point': 'str',
        'currency': 'str',
        'in_dual_mode': 'bool',
        'enable_credit': 'bool',
        'position_initial_margin': 'str',
        'maintenance_margin': 'str',
        'bonus': 'str',
        'history': 'FuturesAccountHistory',
    }

    attribute_map = {
        'total': 'total',
        'unrealised_pnl': 'unrealised_pnl',
        'position_margin': 'position_margin',
        'order_margin': 'order_margin',
        'available': 'available',
        'point': 'point',
        'currency': 'currency',
        'in_dual_mode': 'in_dual_mode',
        'enable_credit': 'enable_credit',
        'position_initial_margin': 'position_initial_margin',
        'maintenance_margin': 'maintenance_margin',
        'bonus': 'bonus',
        'history': 'history',
    }

    def __init__(
        self,
        total=None,
        unrealised_pnl=None,
        position_margin=None,
        order_margin=None,
        available=None,
        point=None,
        currency=None,
        in_dual_mode=None,
        enable_credit=None,
        position_initial_margin=None,
        maintenance_margin=None,
        bonus=None,
        history=None,
        local_vars_configuration=None,
    ):  # noqa: E501
        # type: (str, str, str, str, str, str, str, bool, bool, str, str, str, FuturesAccountHistory, Configuration) -> None
        """FuturesAccount - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._total = None
        self._unrealised_pnl = None
        self._position_margin = None
        self._order_margin = None
        self._available = None
        self._point = None
        self._currency = None
        self._in_dual_mode = None
        self._enable_credit = None
        self._position_initial_margin = None
        self._maintenance_margin = None
        self._bonus = None
        self._history = None
        self.discriminator = None

        if total is not None:
            self.total = total
        if unrealised_pnl is not None:
            self.unrealised_pnl = unrealised_pnl
        if position_margin is not None:
            self.position_margin = position_margin
        if order_margin is not None:
            self.order_margin = order_margin
        if available is not None:
            self.available = available
        if point is not None:
            self.point = point
        if currency is not None:
            self.currency = currency
        if in_dual_mode is not None:
            self.in_dual_mode = in_dual_mode
        if enable_credit is not None:
            self.enable_credit = enable_credit
        if position_initial_margin is not None:
            self.position_initial_margin = position_initial_margin
        if maintenance_margin is not None:
            self.maintenance_margin = maintenance_margin
        if bonus is not None:
            self.bonus = bonus
        if history is not None:
            self.history = history

    @property
    def total(self):
        """Gets the total of this FuturesAccount.  # noqa: E501

        total is the balance after the user's accumulated deposit, withdraw, profit and loss (including realized profit and loss, fund, fee and referral rebate), excluding unrealized profit and loss.  total = SUM(history_dnw, history_pnl, history_fee, history_refr, history_fund)  # noqa: E501

        :return: The total of this FuturesAccount.  # noqa: E501
        :rtype: str
        """
        return self._total

    @total.setter
    def total(self, total):
        """Sets the total of this FuturesAccount.

        total is the balance after the user's accumulated deposit, withdraw, profit and loss (including realized profit and loss, fund, fee and referral rebate), excluding unrealized profit and loss.  total = SUM(history_dnw, history_pnl, history_fee, history_refr, history_fund)  # noqa: E501

        :param total: The total of this FuturesAccount.  # noqa: E501
        :type: str
        """

        self._total = total

    @property
    def unrealised_pnl(self):
        """Gets the unrealised_pnl of this FuturesAccount.  # noqa: E501

        Unrealized PNL  # noqa: E501

        :return: The unrealised_pnl of this FuturesAccount.  # noqa: E501
        :rtype: str
        """
        return self._unrealised_pnl

    @unrealised_pnl.setter
    def unrealised_pnl(self, unrealised_pnl):
        """Sets the unrealised_pnl of this FuturesAccount.

        Unrealized PNL  # noqa: E501

        :param unrealised_pnl: The unrealised_pnl of this FuturesAccount.  # noqa: E501
        :type: str
        """

        self._unrealised_pnl = unrealised_pnl

    @property
    def position_margin(self):
        """Gets the position_margin of this FuturesAccount.  # noqa: E501

        Position margin  # noqa: E501

        :return: The position_margin of this FuturesAccount.  # noqa: E501
        :rtype: str
        """
        return self._position_margin

    @position_margin.setter
    def position_margin(self, position_margin):
        """Sets the position_margin of this FuturesAccount.

        Position margin  # noqa: E501

        :param position_margin: The position_margin of this FuturesAccount.  # noqa: E501
        :type: str
        """

        self._position_margin = position_margin

    @property
    def order_margin(self):
        """Gets the order_margin of this FuturesAccount.  # noqa: E501

        Order margin of unfinished orders  # noqa: E501

        :return: The order_margin of this FuturesAccount.  # noqa: E501
        :rtype: str
        """
        return self._order_margin

    @order_margin.setter
    def order_margin(self, order_margin):
        """Sets the order_margin of this FuturesAccount.

        Order margin of unfinished orders  # noqa: E501

        :param order_margin: The order_margin of this FuturesAccount.  # noqa: E501
        :type: str
        """

        self._order_margin = order_margin

    @property
    def available(self):
        """Gets the available of this FuturesAccount.  # noqa: E501

        The available balance for transferring or trading(including bonus.  Bonus can't be be withdrawn. The transfer amount needs to deduct the bonus)  # noqa: E501

        :return: The available of this FuturesAccount.  # noqa: E501
        :rtype: str
        """
        return self._available

    @available.setter
    def available(self, available):
        """Sets the available of this FuturesAccount.

        The available balance for transferring or trading(including bonus.  Bonus can't be be withdrawn. The transfer amount needs to deduct the bonus)  # noqa: E501

        :param available: The available of this FuturesAccount.  # noqa: E501
        :type: str
        """

        self._available = available

    @property
    def point(self):
        """Gets the point of this FuturesAccount.  # noqa: E501

        POINT amount  # noqa: E501

        :return: The point of this FuturesAccount.  # noqa: E501
        :rtype: str
        """
        return self._point

    @point.setter
    def point(self, point):
        """Sets the point of this FuturesAccount.

        POINT amount  # noqa: E501

        :param point: The point of this FuturesAccount.  # noqa: E501
        :type: str
        """

        self._point = point

    @property
    def currency(self):
        """Gets the currency of this FuturesAccount.  # noqa: E501

        Settle currency  # noqa: E501

        :return: The currency of this FuturesAccount.  # noqa: E501
        :rtype: str
        """
        return self._currency

    @currency.setter
    def currency(self, currency):
        """Sets the currency of this FuturesAccount.

        Settle currency  # noqa: E501

        :param currency: The currency of this FuturesAccount.  # noqa: E501
        :type: str
        """

        self._currency = currency

    @property
    def in_dual_mode(self):
        """Gets the in_dual_mode of this FuturesAccount.  # noqa: E501

        Whether dual mode is enabled  # noqa: E501

        :return: The in_dual_mode of this FuturesAccount.  # noqa: E501
        :rtype: bool
        """
        return self._in_dual_mode

    @in_dual_mode.setter
    def in_dual_mode(self, in_dual_mode):
        """Sets the in_dual_mode of this FuturesAccount.

        Whether dual mode is enabled  # noqa: E501

        :param in_dual_mode: The in_dual_mode of this FuturesAccount.  # noqa: E501
        :type: bool
        """

        self._in_dual_mode = in_dual_mode

    @property
    def enable_credit(self):
        """Gets the enable_credit of this FuturesAccount.  # noqa: E501

        Whether portfolio margin account mode is enabled  # noqa: E501

        :return: The enable_credit of this FuturesAccount.  # noqa: E501
        :rtype: bool
        """
        return self._enable_credit

    @enable_credit.setter
    def enable_credit(self, enable_credit):
        """Sets the enable_credit of this FuturesAccount.

        Whether portfolio margin account mode is enabled  # noqa: E501

        :param enable_credit: The enable_credit of this FuturesAccount.  # noqa: E501
        :type: bool
        """

        self._enable_credit = enable_credit

    @property
    def position_initial_margin(self):
        """Gets the position_initial_margin of this FuturesAccount.  # noqa: E501

        Initial margin position, applicable to the portfolio margin account model  # noqa: E501

        :return: The position_initial_margin of this FuturesAccount.  # noqa: E501
        :rtype: str
        """
        return self._position_initial_margin

    @position_initial_margin.setter
    def position_initial_margin(self, position_initial_margin):
        """Sets the position_initial_margin of this FuturesAccount.

        Initial margin position, applicable to the portfolio margin account model  # noqa: E501

        :param position_initial_margin: The position_initial_margin of this FuturesAccount.  # noqa: E501
        :type: str
        """

        self._position_initial_margin = position_initial_margin

    @property
    def maintenance_margin(self):
        """Gets the maintenance_margin of this FuturesAccount.  # noqa: E501

        Maintenance margin position, applicable to the portfolio margin account model  # noqa: E501

        :return: The maintenance_margin of this FuturesAccount.  # noqa: E501
        :rtype: str
        """
        return self._maintenance_margin

    @maintenance_margin.setter
    def maintenance_margin(self, maintenance_margin):
        """Sets the maintenance_margin of this FuturesAccount.

        Maintenance margin position, applicable to the portfolio margin account model  # noqa: E501

        :param maintenance_margin: The maintenance_margin of this FuturesAccount.  # noqa: E501
        :type: str
        """

        self._maintenance_margin = maintenance_margin

    @property
    def bonus(self):
        """Gets the bonus of this FuturesAccount.  # noqa: E501

        Perpetual Contract Bonus  # noqa: E501

        :return: The bonus of this FuturesAccount.  # noqa: E501
        :rtype: str
        """
        return self._bonus

    @bonus.setter
    def bonus(self, bonus):
        """Sets the bonus of this FuturesAccount.

        Perpetual Contract Bonus  # noqa: E501

        :param bonus: The bonus of this FuturesAccount.  # noqa: E501
        :type: str
        """

        self._bonus = bonus

    @property
    def history(self):
        """Gets the history of this FuturesAccount.  # noqa: E501


        :return: The history of this FuturesAccount.  # noqa: E501
        :rtype: FuturesAccountHistory
        """
        return self._history

    @history.setter
    def history(self, history):
        """Sets the history of this FuturesAccount.


        :param history: The history of this FuturesAccount.  # noqa: E501
        :type: FuturesAccountHistory
        """

        self._history = history

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
        if not isinstance(other, FuturesAccount):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FuturesAccount):
            return True

        return self.to_dict() != other.to_dict()
