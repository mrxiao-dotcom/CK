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


class DualGetOrders(object):
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
        'id': 'int',
        'plan_id': 'int',
        'copies': 'str',
        'invest_amount': 'str',
        'settlement_amount': 'str',
        'create_time': 'int',
        'complete_time': 'int',
        'status': 'str',
        'invest_currency': 'str',
        'exercise_currency': 'str',
        'exercise_price': 'str',
        'settlement_price': 'str',
        'settlement_currency': 'str',
        'apy_display': 'str',
        'apy_settlement': 'str',
        'delivery_time': 'int',
    }

    attribute_map = {
        'id': 'id',
        'plan_id': 'plan_id',
        'copies': 'copies',
        'invest_amount': 'invest_amount',
        'settlement_amount': 'settlement_amount',
        'create_time': 'create_time',
        'complete_time': 'complete_time',
        'status': 'status',
        'invest_currency': 'invest_currency',
        'exercise_currency': 'exercise_currency',
        'exercise_price': 'exercise_price',
        'settlement_price': 'settlement_price',
        'settlement_currency': 'settlement_currency',
        'apy_display': 'apy_display',
        'apy_settlement': 'apy_settlement',
        'delivery_time': 'delivery_time',
    }

    def __init__(
        self,
        id=None,
        plan_id=None,
        copies=None,
        invest_amount=None,
        settlement_amount=None,
        create_time=None,
        complete_time=None,
        status=None,
        invest_currency=None,
        exercise_currency=None,
        exercise_price=None,
        settlement_price=None,
        settlement_currency=None,
        apy_display=None,
        apy_settlement=None,
        delivery_time=None,
        local_vars_configuration=None,
    ):  # noqa: E501
        # type: (int, int, str, str, str, int, int, str, str, str, str, str, str, str, str, int, Configuration) -> None
        """DualGetOrders - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._plan_id = None
        self._copies = None
        self._invest_amount = None
        self._settlement_amount = None
        self._create_time = None
        self._complete_time = None
        self._status = None
        self._invest_currency = None
        self._exercise_currency = None
        self._exercise_price = None
        self._settlement_price = None
        self._settlement_currency = None
        self._apy_display = None
        self._apy_settlement = None
        self._delivery_time = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if plan_id is not None:
            self.plan_id = plan_id
        if copies is not None:
            self.copies = copies
        if invest_amount is not None:
            self.invest_amount = invest_amount
        if settlement_amount is not None:
            self.settlement_amount = settlement_amount
        if create_time is not None:
            self.create_time = create_time
        if complete_time is not None:
            self.complete_time = complete_time
        if status is not None:
            self.status = status
        if invest_currency is not None:
            self.invest_currency = invest_currency
        if exercise_currency is not None:
            self.exercise_currency = exercise_currency
        if exercise_price is not None:
            self.exercise_price = exercise_price
        if settlement_price is not None:
            self.settlement_price = settlement_price
        if settlement_currency is not None:
            self.settlement_currency = settlement_currency
        if apy_display is not None:
            self.apy_display = apy_display
        if apy_settlement is not None:
            self.apy_settlement = apy_settlement
        if delivery_time is not None:
            self.delivery_time = delivery_time

    @property
    def id(self):
        """Gets the id of this DualGetOrders.  # noqa: E501

        Order ID  # noqa: E501

        :return: The id of this DualGetOrders.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this DualGetOrders.

        Order ID  # noqa: E501

        :param id: The id of this DualGetOrders.  # noqa: E501
        :type: int
        """

        self._id = id

    @property
    def plan_id(self):
        """Gets the plan_id of this DualGetOrders.  # noqa: E501

        Plan ID  # noqa: E501

        :return: The plan_id of this DualGetOrders.  # noqa: E501
        :rtype: int
        """
        return self._plan_id

    @plan_id.setter
    def plan_id(self, plan_id):
        """Sets the plan_id of this DualGetOrders.

        Plan ID  # noqa: E501

        :param plan_id: The plan_id of this DualGetOrders.  # noqa: E501
        :type: int
        """

        self._plan_id = plan_id

    @property
    def copies(self):
        """Gets the copies of this DualGetOrders.  # noqa: E501

        Copies  # noqa: E501

        :return: The copies of this DualGetOrders.  # noqa: E501
        :rtype: str
        """
        return self._copies

    @copies.setter
    def copies(self, copies):
        """Sets the copies of this DualGetOrders.

        Copies  # noqa: E501

        :param copies: The copies of this DualGetOrders.  # noqa: E501
        :type: str
        """

        self._copies = copies

    @property
    def invest_amount(self):
        """Gets the invest_amount of this DualGetOrders.  # noqa: E501

        Investment Amount  # noqa: E501

        :return: The invest_amount of this DualGetOrders.  # noqa: E501
        :rtype: str
        """
        return self._invest_amount

    @invest_amount.setter
    def invest_amount(self, invest_amount):
        """Sets the invest_amount of this DualGetOrders.

        Investment Amount  # noqa: E501

        :param invest_amount: The invest_amount of this DualGetOrders.  # noqa: E501
        :type: str
        """

        self._invest_amount = invest_amount

    @property
    def settlement_amount(self):
        """Gets the settlement_amount of this DualGetOrders.  # noqa: E501

        Settlement Amount  # noqa: E501

        :return: The settlement_amount of this DualGetOrders.  # noqa: E501
        :rtype: str
        """
        return self._settlement_amount

    @settlement_amount.setter
    def settlement_amount(self, settlement_amount):
        """Sets the settlement_amount of this DualGetOrders.

        Settlement Amount  # noqa: E501

        :param settlement_amount: The settlement_amount of this DualGetOrders.  # noqa: E501
        :type: str
        """

        self._settlement_amount = settlement_amount

    @property
    def create_time(self):
        """Gets the create_time of this DualGetOrders.  # noqa: E501

        Creation time  # noqa: E501

        :return: The create_time of this DualGetOrders.  # noqa: E501
        :rtype: int
        """
        return self._create_time

    @create_time.setter
    def create_time(self, create_time):
        """Sets the create_time of this DualGetOrders.

        Creation time  # noqa: E501

        :param create_time: The create_time of this DualGetOrders.  # noqa: E501
        :type: int
        """

        self._create_time = create_time

    @property
    def complete_time(self):
        """Gets the complete_time of this DualGetOrders.  # noqa: E501

        Completion Time  # noqa: E501

        :return: The complete_time of this DualGetOrders.  # noqa: E501
        :rtype: int
        """
        return self._complete_time

    @complete_time.setter
    def complete_time(self, complete_time):
        """Sets the complete_time of this DualGetOrders.

        Completion Time  # noqa: E501

        :param complete_time: The complete_time of this DualGetOrders.  # noqa: E501
        :type: int
        """

        self._complete_time = complete_time

    @property
    def status(self):
        """Gets the status of this DualGetOrders.  # noqa: E501

        Status:  `INIT`-INIT `SETTLEMENT_SUCCESS`-Settlement Success `SETTLEMENT_PROCESSING`-SEttlement Processing `CANCELED`-Canceled `FAILED`-Failed  # noqa: E501

        :return: The status of this DualGetOrders.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this DualGetOrders.

        Status:  `INIT`-INIT `SETTLEMENT_SUCCESS`-Settlement Success `SETTLEMENT_PROCESSING`-SEttlement Processing `CANCELED`-Canceled `FAILED`-Failed  # noqa: E501

        :param status: The status of this DualGetOrders.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def invest_currency(self):
        """Gets the invest_currency of this DualGetOrders.  # noqa: E501

        Investment Currency  # noqa: E501

        :return: The invest_currency of this DualGetOrders.  # noqa: E501
        :rtype: str
        """
        return self._invest_currency

    @invest_currency.setter
    def invest_currency(self, invest_currency):
        """Sets the invest_currency of this DualGetOrders.

        Investment Currency  # noqa: E501

        :param invest_currency: The invest_currency of this DualGetOrders.  # noqa: E501
        :type: str
        """

        self._invest_currency = invest_currency

    @property
    def exercise_currency(self):
        """Gets the exercise_currency of this DualGetOrders.  # noqa: E501

        Strike Currency  # noqa: E501

        :return: The exercise_currency of this DualGetOrders.  # noqa: E501
        :rtype: str
        """
        return self._exercise_currency

    @exercise_currency.setter
    def exercise_currency(self, exercise_currency):
        """Sets the exercise_currency of this DualGetOrders.

        Strike Currency  # noqa: E501

        :param exercise_currency: The exercise_currency of this DualGetOrders.  # noqa: E501
        :type: str
        """

        self._exercise_currency = exercise_currency

    @property
    def exercise_price(self):
        """Gets the exercise_price of this DualGetOrders.  # noqa: E501

        Strike price  # noqa: E501

        :return: The exercise_price of this DualGetOrders.  # noqa: E501
        :rtype: str
        """
        return self._exercise_price

    @exercise_price.setter
    def exercise_price(self, exercise_price):
        """Sets the exercise_price of this DualGetOrders.

        Strike price  # noqa: E501

        :param exercise_price: The exercise_price of this DualGetOrders.  # noqa: E501
        :type: str
        """

        self._exercise_price = exercise_price

    @property
    def settlement_price(self):
        """Gets the settlement_price of this DualGetOrders.  # noqa: E501

        settlement price  # noqa: E501

        :return: The settlement_price of this DualGetOrders.  # noqa: E501
        :rtype: str
        """
        return self._settlement_price

    @settlement_price.setter
    def settlement_price(self, settlement_price):
        """Sets the settlement_price of this DualGetOrders.

        settlement price  # noqa: E501

        :param settlement_price: The settlement_price of this DualGetOrders.  # noqa: E501
        :type: str
        """

        self._settlement_price = settlement_price

    @property
    def settlement_currency(self):
        """Gets the settlement_currency of this DualGetOrders.  # noqa: E501

        Settle currency  # noqa: E501

        :return: The settlement_currency of this DualGetOrders.  # noqa: E501
        :rtype: str
        """
        return self._settlement_currency

    @settlement_currency.setter
    def settlement_currency(self, settlement_currency):
        """Sets the settlement_currency of this DualGetOrders.

        Settle currency  # noqa: E501

        :param settlement_currency: The settlement_currency of this DualGetOrders.  # noqa: E501
        :type: str
        """

        self._settlement_currency = settlement_currency

    @property
    def apy_display(self):
        """Gets the apy_display of this DualGetOrders.  # noqa: E501

        APY  # noqa: E501

        :return: The apy_display of this DualGetOrders.  # noqa: E501
        :rtype: str
        """
        return self._apy_display

    @apy_display.setter
    def apy_display(self, apy_display):
        """Sets the apy_display of this DualGetOrders.

        APY  # noqa: E501

        :param apy_display: The apy_display of this DualGetOrders.  # noqa: E501
        :type: str
        """

        self._apy_display = apy_display

    @property
    def apy_settlement(self):
        """Gets the apy_settlement of this DualGetOrders.  # noqa: E501

        Settlement APY  # noqa: E501

        :return: The apy_settlement of this DualGetOrders.  # noqa: E501
        :rtype: str
        """
        return self._apy_settlement

    @apy_settlement.setter
    def apy_settlement(self, apy_settlement):
        """Sets the apy_settlement of this DualGetOrders.

        Settlement APY  # noqa: E501

        :param apy_settlement: The apy_settlement of this DualGetOrders.  # noqa: E501
        :type: str
        """

        self._apy_settlement = apy_settlement

    @property
    def delivery_time(self):
        """Gets the delivery_time of this DualGetOrders.  # noqa: E501

        Settlement time  # noqa: E501

        :return: The delivery_time of this DualGetOrders.  # noqa: E501
        :rtype: int
        """
        return self._delivery_time

    @delivery_time.setter
    def delivery_time(self, delivery_time):
        """Sets the delivery_time of this DualGetOrders.

        Settlement time  # noqa: E501

        :param delivery_time: The delivery_time of this DualGetOrders.  # noqa: E501
        :type: int
        """

        self._delivery_time = delivery_time

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
        if not isinstance(other, DualGetOrders):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DualGetOrders):
            return True

        return self.to_dict() != other.to_dict()
