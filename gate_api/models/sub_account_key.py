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


class SubAccountKey(object):
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
        'user_id': 'str',
        'mode': 'int',
        'name': 'str',
        'perms': 'list[ApiV4KeyPerm]',
        'ip_whitelist': 'list[str]',
        'key': 'str',
        'state': 'int',
        'created_at': 'str',
        'updated_at': 'str',
    }

    attribute_map = {
        'user_id': 'user_id',
        'mode': 'mode',
        'name': 'name',
        'perms': 'perms',
        'ip_whitelist': 'ip_whitelist',
        'key': 'key',
        'state': 'state',
        'created_at': 'created_at',
        'updated_at': 'updated_at',
    }

    def __init__(
        self,
        user_id=None,
        mode=None,
        name=None,
        perms=None,
        ip_whitelist=None,
        key=None,
        state=None,
        created_at=None,
        updated_at=None,
        local_vars_configuration=None,
    ):  # noqa: E501
        # type: (str, int, str, list[ApiV4KeyPerm], list[str], str, int, str, str, Configuration) -> None
        """SubAccountKey - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._user_id = None
        self._mode = None
        self._name = None
        self._perms = None
        self._ip_whitelist = None
        self._key = None
        self._state = None
        self._created_at = None
        self._updated_at = None
        self.discriminator = None

        if user_id is not None:
            self.user_id = user_id
        if mode is not None:
            self.mode = mode
        if name is not None:
            self.name = name
        if perms is not None:
            self.perms = perms
        if ip_whitelist is not None:
            self.ip_whitelist = ip_whitelist
        if key is not None:
            self.key = key
        if state is not None:
            self.state = state
        if created_at is not None:
            self.created_at = created_at
        if updated_at is not None:
            self.updated_at = updated_at

    @property
    def user_id(self):
        """Gets the user_id of this SubAccountKey.  # noqa: E501

        User ID  # noqa: E501

        :return: The user_id of this SubAccountKey.  # noqa: E501
        :rtype: str
        """
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        """Sets the user_id of this SubAccountKey.

        User ID  # noqa: E501

        :param user_id: The user_id of this SubAccountKey.  # noqa: E501
        :type: str
        """

        self._user_id = user_id

    @property
    def mode(self):
        """Gets the mode of this SubAccountKey.  # noqa: E501

        Mode: 1 - classic 2 - portfolio account  # noqa: E501

        :return: The mode of this SubAccountKey.  # noqa: E501
        :rtype: int
        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Sets the mode of this SubAccountKey.

        Mode: 1 - classic 2 - portfolio account  # noqa: E501

        :param mode: The mode of this SubAccountKey.  # noqa: E501
        :type: int
        """

        self._mode = mode

    @property
    def name(self):
        """Gets the name of this SubAccountKey.  # noqa: E501

        API key name  # noqa: E501

        :return: The name of this SubAccountKey.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this SubAccountKey.

        API key name  # noqa: E501

        :param name: The name of this SubAccountKey.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def perms(self):
        """Gets the perms of this SubAccountKey.  # noqa: E501


        :return: The perms of this SubAccountKey.  # noqa: E501
        :rtype: list[ApiV4KeyPerm]
        """
        return self._perms

    @perms.setter
    def perms(self, perms):
        """Sets the perms of this SubAccountKey.


        :param perms: The perms of this SubAccountKey.  # noqa: E501
        :type: list[ApiV4KeyPerm]
        """

        self._perms = perms

    @property
    def ip_whitelist(self):
        """Gets the ip_whitelist of this SubAccountKey.  # noqa: E501

        ip white list (list will be removed if no value is passed)  # noqa: E501

        :return: The ip_whitelist of this SubAccountKey.  # noqa: E501
        :rtype: list[str]
        """
        return self._ip_whitelist

    @ip_whitelist.setter
    def ip_whitelist(self, ip_whitelist):
        """Sets the ip_whitelist of this SubAccountKey.

        ip white list (list will be removed if no value is passed)  # noqa: E501

        :param ip_whitelist: The ip_whitelist of this SubAccountKey.  # noqa: E501
        :type: list[str]
        """

        self._ip_whitelist = ip_whitelist

    @property
    def key(self):
        """Gets the key of this SubAccountKey.  # noqa: E501

        API Key  # noqa: E501

        :return: The key of this SubAccountKey.  # noqa: E501
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this SubAccountKey.

        API Key  # noqa: E501

        :param key: The key of this SubAccountKey.  # noqa: E501
        :type: str
        """

        self._key = key

    @property
    def state(self):
        """Gets the state of this SubAccountKey.  # noqa: E501

        State 1 - normal 2 - locked 3 - frozen  # noqa: E501

        :return: The state of this SubAccountKey.  # noqa: E501
        :rtype: int
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this SubAccountKey.

        State 1 - normal 2 - locked 3 - frozen  # noqa: E501

        :param state: The state of this SubAccountKey.  # noqa: E501
        :type: int
        """

        self._state = state

    @property
    def created_at(self):
        """Gets the created_at of this SubAccountKey.  # noqa: E501

        Creation time  # noqa: E501

        :return: The created_at of this SubAccountKey.  # noqa: E501
        :rtype: str
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this SubAccountKey.

        Creation time  # noqa: E501

        :param created_at: The created_at of this SubAccountKey.  # noqa: E501
        :type: str
        """

        self._created_at = created_at

    @property
    def updated_at(self):
        """Gets the updated_at of this SubAccountKey.  # noqa: E501

        Last update time  # noqa: E501

        :return: The updated_at of this SubAccountKey.  # noqa: E501
        :rtype: str
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this SubAccountKey.

        Last update time  # noqa: E501

        :param updated_at: The updated_at of this SubAccountKey.  # noqa: E501
        :type: str
        """

        self._updated_at = updated_at

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
        if not isinstance(other, SubAccountKey):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SubAccountKey):
            return True

        return self.to_dict() != other.to_dict()
