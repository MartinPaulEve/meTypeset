#!/usr/bin/env python
# @Author Dulip Withanage


import os
import shutil
from debug import *
import ntpath

# class Global Variables
class GV (Debuggable):
    def __init__(self, settings, debug):
        self.debug = debug
        Debuggable.__init__(self, 'Globals')

        # todo: clean this up -- it's a mess

        docx = 'docx'
        common2 = 'common2'
        nlm = 'nlm'
        chain = 'xsl'
        error = 'error'
        db = 'databasefile'

        self.settings = settings

        self.script_dir = os.environ['METYPESET']

        if not settings.args['bibscan']:

            self.input_file_path = settings.args['<input>'].strip()

            self.input_metadata_file_path = settings.args['--metadata'] if settings.args[
                '--metadata'] else os.path.join(settings.script_dir,
                                                settings.value_for_tag(settings, 'default-metadata-file-path', self))

            filename_sep = ntpath.basename(self.input_file_path)
            self.output_folder_path = os.path.expanduser(settings.args['<output_folder>'])

            #general directory paths
            self.runtime_folder_path = self.generate_path(settings, 'runtime', settings.script_dir)
            self.common2_lib_path = self.generate_path(settings, common2, settings.script_dir)
            self.binary_folder_path = self.generate_path(settings, 'binaries', settings.script_dir)
            self.runtime_catalog_path = self.generate_path(settings, 'runtime-catalog', settings.script_dir)
            self.common2_temp_folder_path = self.generate_path(settings, common2, self.output_folder_path)

            # docx document paths
            self.docx_folder_path = self.generate_path(settings, docx, settings.script_dir)

            self.docx_temp_folder_path = self.generate_path(settings, docx, self.output_folder_path)

            self.docx_word_temp_folder_path = settings.clean_path(
                settings.concat_path(self.docx_temp_folder_path, settings.value_for_tag(settings, 'word', self)))

            self.word_document_xml = settings.clean_path(
                self.docx_temp_folder_path + '/' + settings.value_for_tag(settings, 'word-document-xml', self))

            self.docx_style_sheet_dir = settings.concat_path(self.script_dir,
                                                             settings.value_for_tag(settings, 'docs-style-sheet-path',
                                                                                    self))
            self.proprietary_style_sheet = settings.concat_path(self.script_dir,
                                                                settings.value_for_tag(settings,
                                                                                       'proprietary-math-stylesheet',
                                                                                       self))

            self.docx_to_tei_stylesheet = settings.clean_path(
                self.docx_temp_folder_path + '/' + settings.value_for_tag(settings, 'doc-to-tei-stylesheet', self))

            self.docx_media_path = settings.clean_path(
                settings.concat_path(self.docx_word_temp_folder_path, settings.value_for_tag(settings, 'media', self)))

            self.output_media_path = settings.clean_path(
                settings.concat_path(self.output_folder_path, settings.value_for_tag(settings, 'outputmedia', self)))

            #OUTPUT FILE
            if os.path.isdir(self.input_file_path):
                self.file_name = 'tei.xml'
            else:
                fileName, fileExtension = os.path.splitext(filename_sep)
                self.file_name = fileName + os.path.extsep + 'xml'

            #TEI paths
            self.tei_folder_path = settings.clean_path(self.output_folder_path + '/' + settings.value_for_tag(settings,
                                                                                                              'tei',
                                                                                                              self))
            self.tei_file_path = settings.concat_path(self.tei_folder_path, self.file_name)
            self.tei_temp_file_path = settings.clean_path(settings.concat_path(self.tei_folder_path, "out.xml"))

            #NLM paths
            self.nlm_folder_path = self.generate_path(settings, nlm, self.output_folder_path)
            self.nlm_file_path = settings.clean_path(settings.concat_path(self.nlm_folder_path, self.file_name))
            self.nlm_temp_file_path = settings.clean_path(settings.concat_path(self.nlm_folder_path, "out.xml"))
            self.nlm_style_sheet_dir = settings.clean_path(settings.concat_path(settings.script_dir,
                                                                        settings.value_for_tag(settings,
                                                                                           'tei-to-nlm-stylesheet',
                                                                                           self)))

            # XSL chain paths
            self.xsl_folder_path = self.generate_path(settings, chain, self.output_folder_path)
            self.xsl_file_path = settings.clean_path(settings.concat_path(self.xsl_folder_path, "out.html"))


            # error log chain paths
            self.error_folder_path = self.generate_path(settings, error, self.output_folder_path)
            self.error_file_path = settings.clean_path(settings.concat_path(self.error_folder_path, "errors.txt"))

            #Metadata paths
            self.metadata_style_sheet_path = settings.clean_path(
                settings.concat_path(settings.script_dir, settings.value_for_tag(settings, 'metadata-stylesheet',
                                                                                 self)))

            #java classes for saxon
            self.java_class_path = self.set_java_classpath()

        else:
            self.nlm_file_path = ''
            self.nlm_temp_file_path = ''

        # database paths
        self.database_file_path = settings.clean_path(settings.concat_path(os.path.join(settings.script_dir, 'database'),
                                                                   settings.value_for_tag(self.settings,
                                                                                      'databasefile', self)))

    def check_file_exists(self, file_path):
        if file_path is None:
            self.debug.print_debug(self, 'An empty file path was passed')
        try:
            os.path.isfile(file_path)
        except:
            self.debug.fatal_error(self, 'Unable to locate {0}'.format(file_path))

    def generate_path(self, settings, tag, path):
        return settings.clean_path(settings.concat_path(path, settings.value_for_tag(settings, tag, self)))

    def mk_dir(self, path):
        self.debug.mkdir(path)

    def setting(self, tag):
        return self.settings.value_for_tag(self.settings, tag, self)

    @staticmethod
    def copy_folder(src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = str(os.path.join(src, item))
            d = str(os.path.join(dst, item))
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                #print s ,d
                shutil.copy(s, d)

    def set_java_classpath(self):
        java_class_path = ''
        #runtime_dir = concat_path(script_dir,value_for_tag(settings,'runtime'))
        for lib in self.settings.value_for_tag(self.settings, 'saxon-libs', self).strip().split(";"):
            self.check_file_exists(self.settings.concat_path(self.runtime_folder_path, lib))
            java_class_path += self.settings.concat_path(self.runtime_folder_path, lib)
            java_class_path += ":"
        return '"' + java_class_path.rstrip(':') + '"'

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False