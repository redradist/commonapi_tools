import re

_type_regex = re.compile(r"([\.\w]+)\s*(\[\])?")


def _upper_case_first_letter(name):
    """
    Function that convert first character of name to UPPER case
    :param name: String which first character will be converted to UPPER case
    :return: String with first character in UPPER case
    """
    indices = set([0])
    return "".join(c.upper() if i in indices else c for i, c in enumerate(name))


def _cpp_type_from(type_namespace, type):
    """
    Function that convert cpp type to commonapi type
    :param type_namespace: Namespace of type
    :param type: cpp type
    :return: commonapi type
    """
    is_array = False
    real_type = None
    matchs = _type_regex.findall(type)
    if matchs:
        if matchs[0]:
            if matchs[0][0]:
                real_type = matchs[0][0]
            if matchs[0][1]:
                is_array = True
    real_type = real_type.replace(".", "::")
    if real_type == "Int8":
        real_type = "int8_t"
    elif real_type == "UInt8":
        real_type = "uint8_t"
    elif real_type == "Int16":
        real_type = "int16_t"
    elif real_type == "UInt16":
        real_type = "uint16_t"
    elif real_type == "Int32":
        real_type = "int32_t"
    elif real_type == "UInt32":
        real_type = "uint32_t"
    elif real_type == "String":
        real_type = "std::string"
    elif type_namespace and len(real_type) > 0 and real_type[0] == 't':
        real_type = type_namespace + "::" + real_type
    if is_array:
        return 'std::vector<' + real_type + '>'
    else:
        return real_type


class Parameter:
    """
    Class for collecting information regarding the parameter meta-information
    """
    def __init__(self, type_namespace, type, name, description):
        """
        Class for collecting information regarding the parameter meta-information
        :param type_namespace:
        :param type:
        :param name:
        """
        self.type_namespace = type_namespace
        self.type = _cpp_type_from(self.type_namespace, type)
        self.name = name
        self.description = description

    def __repr__(self):
        """
        Detail string representation of Parameter class
        :return: Detail string representation
        """
        result = ""
        result += "Parameter type: " + str(self.type) + "\n"
        result += "Parameter name: " + str(self.name) + "\n"
        return result

    def __str__(self):
        """
        Detail string representation of Parameter class
        :return: Parameter name
        """
        return self.name


class Attribute(Parameter):
    """
    Class for collecting information regarding the attribute meta-information
    """
    def __init__(self, type_namespace,  type, name, description):
        Parameter.__init__(self, type_namespace, type, name, description)
        self.name = _upper_case_first_letter(self.name)
        self.description = description

    def upper(self):
        return str(self).upper()

    def lower(self):
        return str(self).lower()

    def __repr__(self):
        """
        Detail string representation of Attribute class
        :return: Detail string representation
        """
        result = ""
        result += "Attribute type: " + str(self.type) + "\n"
        result += "Attribute name: " + str(self.name) + "\n"
        return result

    def __str__(self):
        """
        String representation of Attribute class
        :return: Attribute name
        """
        return self.name


class Broadcast:
    """
    Class for collecting information regarding the broadcast meta-information
    """
    def __init__(self, name, description):
        self.name = _upper_case_first_letter(name)
        self.parameters = []
        self.description = description

    def upper(self):
        return str(self).upper()

    def lower(self):
        return str(self).lower()

    def __repr__(self):
        """
        Detail string representation of Broadcast class
        :return: Detail string representation
        """
        result = ""
        result += "Broadcast name: " + str(self.name) + "\n"
        if self.parameters:
            for param in self.parameters:
                result += str(param) + "\n"
        return result

    def __str__(self):
        """
        String representation of Broadcast class
        :return: Broadcast name
        """
        return self.name


class Method:
    """
    Class for collecting information regarding the method meta-information
    """
    def __init__(self, name, description):
        self.name = name
        self.inputs = []
        self.outputs = None
        self.description = description

    def __repr__(self):
        """
        Detail string representation of Method class
        :return: Detail string representation
        """
        result = ""
        result += "Method name: " + str(self.name) + "\n"
        if self.inputs:
            for param in self.inputs:
                result += str(param) + "\n"
        if self.outputs:
            for param in self.outputs:
                result += str(param) + "\n"
        return result

    def __str__(self):
        """
        String representation of Method class
        :return: Method name
        """
        return _upper_case_first_letter(self.name)


class Interface:
    """
    Class for collecting information regarding the interface meta-information
    """
    def __init__(self, name, description):
        self.package_name = None
        self.major = None
        self.minor = None
        self.description = description
        self.name = name
        self.methods = []
        self.broadcasts = []
        self.attributes = []

    def set_package_name(self, package_name):
        """
        Set package name
        :param package_name: Package name
        :return: None
        """
        self.package_name = package_name

    def set_major(self, major):
        """
        Set major version of interface
        :param major: Major version
        :return: None
        """
        self.major = major

    def set_minor(self, minor):
        """
        Set minor version of interface
        :param minor: Minor version
        :return: None
        """
        self.minor = minor

    def __repr__(self):
        """
        Detail string representation of Interface class
        :return: Detail string representation
        """
        result = ""
        result += str(self.package_name) + "\n"
        result += "Interface name: " + str(self.name) + "\n"
        for method in self.methods:
            result += str(method) + "\n"
        for broadcast in self.broadcasts:
            result += str(broadcast) + "\n"
        for attribute in self.attributes:
            result += str(attribute) + "\n"
        return self.name

    def __str__(self):
        """
        String representation of Interface class
        :return: Interface name
        """
        return self.name
