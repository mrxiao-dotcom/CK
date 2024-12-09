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


class StructuredOrderList(object):
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
        'pid': 'str',
        'lock_coin': 'str',
        'amount': 'str',
        'status': 'str',
        'income': 'str',
        'create_time': 'int',
    }

    attribute_map = {
        'id': 'id',
        'pid': 'pid',
        'lock_coin': 'lock_coin',
        'amount': 'amount',
        'status': 'status',
        'income': 'income',
        'create_time': 'create_time',
    }

    def __init__(
        self,
        id=None,
        pid=None,
        lock_coin=None,
        amount=None,
        status=None,
        income=None,
        create_time=None,
        local_vars_configuration=None,
    ):  # noqa: E501
        # type: (int, str, str, str, str, str, int, Configuration) -> None
        """StructuredOrderList - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._pid = None
        self._lock_coin = None
        self._amount = None
        self._status = None
        self._income = None
        self._create_time = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if pid is not None:
            self.pid = pid
        if lock_coin is not None:
            self.lock_coin = lock_coin
        if amount is not None:
            self.amount = amount
        if status is not None:
            self.status = status
        if income is not None:
            self.income = income
        if create_time is not None:
            self.create_time = create_time

    @property
    def id(self):
        """Gets the id of this StructuredOrderList.  # noqa: E501

        Order ID  # noqa: E501

        :return: The id of this StructuredOrderList.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this StructuredOrderList.

        Order ID  # noqa: E501

        :param id: The id of this StructuredOrderList.  # noqa: E501
        :type: int
        """

        self._id = id

    @property
    def pid(self):
        """Gets the pid of this StructuredOrderList.  # noqa: E501

        Plan ID  # noqa: E501

        :return: The pid of this StructuredOrderList.  # noqa: E501
        :rtype: str
        """
        return self._pid

    @pid.setter
    def pid(self, pid):
        """Sets the pid of this StructuredOrderList.

        Plan ID  # noqa: E501

        :param pid: The pid of this StructuredOrderList.  # noqa: E501
        :type: str
        """

        self._pid = pid

    @property
    def lock_coin(self):
        """Gets the lock_coin of this StructuredOrderList.  # noqa: E501

        Locked coin  # noqa: E501

        :return: The lock_coin of this StructuredOrderList.  # noqa: E501
        :rtype: str
        """
        return self._lock_coin

    @lock_coin.setter
    def lock_coin(self, lock_coin):
        """Sets the lock_coin of this StructuredOrderList.

        Locked coin  # noqa: E501

        :param lock_coin: The lock_coin of this StructuredOrderList.  # noqa: E501
        :type: str
        """

        self._lock_coin = lock_coin

    @property
    def amount(self):
        """Gets the amount of this StructuredOrderList.  # noqa: E501

        Locked amount  # noqa: E501

        :return: The amount of this StructuredOrderList.  # noqa: E501
        :rtype: str
        """
        return self._amount

    @amount.setter
    def amount(self, amount):
        """Sets the amount of this StructuredOrderList.

        Locked amount  # noqa: E501

        :param amount: The amount of this StructuredOrderList.  # noqa: E501
        :type: str
        """

        self._amount = amount

    @property
    def status(self):
        """Gets the status of this StructuredOrderList.  # noqa: E501

        Status:   SUCCESS - SUCCESS  FAILED - FAILED DONE - DONE  # noqa: E501

        :return: The status of this StructuredOrderList.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this StructuredOrderList.

        Status:   SUCCESS - SUCCESS  FAILED - FAILED DONE - DONE  # noqa: E501

        :param status: The status of this StructuredOrderList.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def income(self):
        """Gets the income of this StructuredOrderList.  # noqa: E501

        Income  # noqa: E501

        :return: The income of this StructuredOrderList.  # noqa: E501
        :rtype: str
        """
        return self._income

    @income.setter
    def income(self, income):
        """Sets the income of this StructuredOrderList.

        Income  # noqa: E501

        :param income: The income of this StructuredOrderList.  # noqa: E501
        :type: str
        """

        self._income = income

    @property
    def create_time(self):
        """Gets the create_time of this StructuredOrderList.  # noqa: E501

        Created time  # noqa: E501

        :return: The create_time of this StructuredOrderList.  # noqa: E501
        :rtype: int
        """
        return self._create_time

    @create_time.setter
    def create_time(self, create_time):
        """Sets the create_time of this StructuredOrderList.

        Created time  # noqa: E501

        :param create_time: The create_time of this StructuredOrderList.  # noqa: E501
        :type: int
        """

        self._create_time = create_time

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
        if not isinstance(other, StructuredOrderList):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, StructuredOrderList):
            return True

        return self.to_dict() != other.to_dict()
