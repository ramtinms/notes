import json
import re


class SimplePython3Parser():

    def __init__(self):
        self.import_pattern1 = re.compile("^import ([\w\,\. ]+)$")
        self.import_pattern2 = re.compile("^from ([\w\,\. ]+) import ([\w\,\. ]+)$")
        self.class_pattern1 = re.compile("^class ([\w]+)[ ]*:$")
        self.method_pattern1 = re.compile("^|\W+def ([\w\,\(\)\=]+)[ ]*:$")

    def match_import(self, line):
        packages = []
        match = self.import_pattern1.search(line)
        if match:
            lib = match.group(1)
            if ',' in lib:
                lib = re.sub('\, +', ', ', lib)
                libs = lib.split(',')
                for item in libs:
                    packages.append(item)
            else:
                packages.append(lib)

        match = self.import_pattern2.search(line)
        if match:
            parentlib = match.group(1)
            lib = match.group(2)
            if ',' in lib:
                lib = re.sub('\, +', ', ', lib)
                libs = lib.split(',')
                for item in libs:
                    packages.append(parentlib + '.' + item)
            else:
                packages.append(parentlib + '.' + lib)
        return packages

    def match_class(self, line):
        classes = []
        match = self.class_pattern1.search(line)
        if match:
            class_name = match.group(1)
            classes.append(class_name)
        return classes

    def process(self,
                text,
                get_packages=True,
                get_classes=True,
                get_methods=False):

        packages = []
        classes = []
        methods = []

        # break to lines
        lines = text.strip().split('\n')

        for line in lines:
            cleaned_line = line.strip().lstrip()

            if get_packages:
                packages += self.match_import(cleaned_line)

            if get_classes:
                classes += self.match_class(cleaned_line)

        return (packages, classes, methods)

    def test_match_import(self):
        test = """
                import sys, os\n
                import datetime"""

        res = self.match_import(test)
        assert res == ['sys', 'os', 'datetime']

        test = "import datetime\n"
        res = self.match_import(test)
        assert res == ['datetime']

        test = 'from datetime import datetime\n'
        res = self.match_import(test)
        assert res == ['datetime.datetime']

    def test_match_class(self):
        test = 'class Test:\n'
        res = self.match_import(test)
        assert res == ['Test']
