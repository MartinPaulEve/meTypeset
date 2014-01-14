__author__ = 'martin'

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

from lxml import etree
import uuid
from copy import deepcopy
import shutil
from lxml import objectify
import re
from debug import Debuggable

class Manipulate(Debuggable):
    def __init__(self, gv):
        self.gv = gv
        self.debug = self.gv.debug
        Debuggable.__init__(self, '{0} Manipulator'.format(self.mod_name))

    @staticmethod
    def set_dom_tree(filename):
        p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)

        return etree.parse(filename, p)

    @staticmethod
    def update_tmp_file(fr, to):
        shutil.copy2(fr, to)

    @staticmethod
    def get_file_text(filename):
        f = open(filename)
        text = f.read()
        f.close()
        return text

    @staticmethod
    def xml_start(tag):
        return '<' + tag + '>'

    @staticmethod
    def xml_end(tag):
        return '</' + tag + '>'

    @staticmethod
    def search_and_replace_dom(tree, search_section, search_element, surround_with):
        for p in tree.xpath(".//" + search_section):
            search_results = p.findall(".//" + search_element)
            i = 0
            for result in search_results:
                i += 1
                new_elem = etree.Element(surround_with)
                new_elem.set("order", str(i))
                new_elem.set("uuid", str(uuid.uuid4()))
                if len(result) > 0:
                    elem_copy = deepcopy(result[0])
                    result.clear()
                    new_elem.append(elem_copy)
                    result.append(new_elem)
                else:
                    new_elem.text = result.text
                    result.clear()
                    result.append(new_elem)
        return tree

    @staticmethod
    def write_output(f, text):
        out = open(f, 'w')
        out.write(text)
        out.close()

    # Returns the value after a searching a list of regex or None if nothing found.
    @staticmethod
    def try_list_of_regex(file_string, *regex):
        if len(regex) > 0:
            for i in regex:
                val = re.findall(file_string, i)
                if val:
                    return val
            return None
        else:
            return None

    @staticmethod
    def replace_value_of_tag(text, new_value):
        obj = objectify.fromstring(text)
        # noinspection PyProtectedMember
        obj.teiHeader.fileDesc.titleStmt.title._setText(new_value)
        return etree.tostring(obj.getroottree())

    def load_dom_tree(self):
        # load the DOM
        self.update_tmp_file(self.dom_to_load, self.dom_temp_file)
        tree = self.set_dom_tree(self.dom_temp_file)
        return tree

    # replaces a given tag with a list of replace tags
    def replace(self, text, tag, *params):
        replace_start = ''
        replace_end = ''

        if len(params) > 0:
            for i in params:
                replace_start += self.xml_start(i)
                replace_end += self.xml_end(i)

            text = text.replace(self.xml_start(tag), replace_start).replace(self.xml_end(tag), replace_end)

        else:
            self.debug.print_debug(self, "No parameters passed to replace function")
        return text