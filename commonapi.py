import re

_type_regex = re.compile(r"([\.\w]+)\s*(\[\])?")


def _upper_case_first_letter(name):
    indices = set([0])
    return "".join(c.upper() if i in indices else c for i, c in enumerate(name))


def _cpp_type_from(type_namespace, type):
    """

    :param type:
    :return:
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
    Class described
    """
    def __init__(self, type_namespace, type, name, description):
        """

        :param type:
        :param name:
        """
        self.type_namespace = type_namespace
        self.type = _cpp_type_from(self.type_namespace, type)
        self.name = name
        self.description = description

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
    def __init__(self, type_namespace,  type, name, description):
        Parameter.__init__(self, type_namespace, type, name, description)
        self.name = _upper_case_first_letter(self.name)
        self.description = description

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
    def __init__(self, name, description):
        self.name = _upper_case_first_letter(name)
        self.parameters = []
        self.description = description

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
    def __init__(self, name, description):
        self.name = name
        self.inputs = []
        self.outputs = None
        self.description = description

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
    def __init__(self, name, description):
        self.package_name = None
        self.major = None
        self.minor = None
        self.name = name
        self.methods = []
        self.broadcasts = []
        self.attributes = []
        self.description = description

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key == "methods":
            for method in self.methods:
                if method.inputs:
                    for input in method.inputs:
                        input.type_namespace = self.name
                if method.outputs:
                    for output in method.outputs:
                        output.type_namespace = self.name
        elif key == "broadcasts":
            for broadcast in self.broadcasts:
                if broadcast.parameters:
                    for parameter in broadcast.parameters:
                        parameter.type_namespace = self.name
        elif key == "attributes":
            for attribute in self.attributes:
                attribute.type_namespace = self.name

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
