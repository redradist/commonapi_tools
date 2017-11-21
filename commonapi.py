import re

_type_regex = re.compile(r"([\.\w]+)\s*(\[\])?")


def _upper_case_first_letter(name):
    indices = set([0])
    return "".join(c.upper() if i in indices else c for i, c in enumerate(name))


def _cpp_type_from(type):
    """

    :param type:
    :return:
    """
    is_array = False
    real_type = None
    matchs = _type_regex.findall(type)
    if matchs:
        print(str(matchs))
        if matchs[0]:
            if matchs[0][0]:
                real_type = matchs[0][0]
            if matchs[0][1]:
                is_array = True
    real_type = real_type.replace(".", "::")
    real_type = real_type.replace("String", "std::string")
    real_type = real_type.replace("Int8", "int8_t")
    real_type = real_type.replace("UInt8", "uint8_t")
    real_type = real_type.replace("Int16", "int16_t")
    real_type = real_type.replace("UInt16", "uint16_t")
    real_type = real_type.replace("Int32", "int32_t")
    real_type = real_type.replace("UInt32", "uint32_t")
    real_type = real_type.replace("String", "std::string")
    print("real_type is " + real_type)
    if is_array:
        return 'std::vector<' + real_type + '>'
    else:
        return real_type


class Parameter:
    """
    Class described
    """
    def __init__(self, type, name):
        """

        :param type:
        :param name:
        """
        self.type = _cpp_type_from(type)
        self.name = name

    def __str__(self):
        """

        :return:
        """
        result = ""
        result += "Parameter type: " + str(self.type) + "\n"
        result += "Parameter name: " + str(self.name) + "\n"
        return result


class Attribute(Parameter):
    """
    Class described
    """
    def __init__(self, type, name):
        Parameter.__init__(self, type, name)
        self.name = _upper_case_first_letter(self.name)

    def __str__(self):
        """

        :return:
        """
        # result = ""
        # result += "Attribute type: " + str(self.type) + "\n"
        # result += "Attribute name: " + str(self.name) + "\n"
        return self.name

    def upper(self):
        return str(self).upper()

    def lower(self):
        return str(self).lower()


class Broadcast:
    """
    Class described
    """
    def __init__(self, name):
        self.name = _upper_case_first_letter(name)
        self.parameters = []

    def __str__(self):
        """

        :return:
        """
        # result = ""
        # result += "Broadcast name: " + str(self.name) + "\n"
        # if self.parameters:
        #     for param in self.parameters:
        #         result += str(param) + "\n"
        return self.name

    def upper(self):
        return str(self).upper()

    def lower(self):
        return str(self).lower()


class Method:
    """
    Class described
    """
    def __init__(self, name):
        self.name = name
        self.inputs = []
        self.outputs = None

    def __str__(self):
        """

        :return:
        """
        # result = ""
        # result += "Method name: " + str(self.name) + "\n"
        # if self.inputs:
        #     for param in self.inputs:
        #         result += str(param) + "\n"
        # if self.outputs:
        #     for param in self.outputs:
        #         result += str(param) + "\n"
        return _upper_case_first_letter(self.name)


class Interface:
    """
    Class described
    """
    def __init__(self, name):
        self.package_name = None
        self.major = None
        self.minor = None
        self.name = name
        self.methods = []
        self.broadcasts = []
        self.attributes = []

    def set_package_name(self, package_name):
        """

        :param package_name:
        :return:
        """
        self.package_name = package_name

    def set_major(self, major):
        """

        :param major:
        :return:
        """
        self.major = major

    def set_minor(self, minor):
        """

        :param minor:
        :return:
        """
        self.minor = minor

    def __str__(self):
        """

        :return:
        """
        # result = ""
        # result += str(self.package_name) + "\n"
        # result += "Interface name: " + str(self.name) + "\n"
        # for method in self.methods:
        #     result += str(method) + "\n"
        # for broadcast in self.broadcasts:
        #     result += str(broadcast) + "\n"
        # for attribute in self.attributes:
        #     result += str(attribute) + "\n"
        return self.name
