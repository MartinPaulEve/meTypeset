#-*- coding:utf-8 -*-

"""
Originally (c) Sebastiaan Mathot 2011
Modifications (c) 2014 Martin Paul Eve

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

import sqlite3
import os
import os.path
import sys
import shutil
import sys
import time
from zotero_item import zoteroItem as zotero_item
from debug import Debuggable


class LibZotero(Debuggable):
    """
    Libzotero provides access to the zotero database.
    This is an object oriented reimplementation of the
    original zoterotools.
    """

    attachment_query = u"""
		select items.itemID, itemAttachments.path, itemAttachments.itemID
		from items, itemAttachments
		where items.itemID = itemAttachments.sourceItemID
		"""

    info_query = u"""
		select items.itemID, fields.fieldName, itemDataValues.value, items.key, itemTypes.typeName
		from items, itemData, fields, itemDataValues, itemTypes
		where
			items.itemID = itemData.itemID
			and itemData.fieldID = fields.fieldID
			and itemData.valueID = itemDataValues.valueID
			and itemTypes.itemTypeID = items.itemTypeID
		"""

    collection_query = u"""
		select items.itemID, collections.collectionName
		from items, collections, collectionItems
		where
			items.itemID = collectionItems.itemID
			and collections.collectionID = collectionItems.collectionID
		order by collections.collectionName != "To Read",
			collections.collectionName
		"""

    tag_query = u"""
		select items.itemID, tags.name
		from items, tags, itemTags
		where
			items.itemID = itemTags.itemID
			and tags.tagID = itemTags.tagID
		"""

    deleted_query = u"select itemID from deletedItems"

    @staticmethod
    def creator_query(creator_type):
        return u"""
		select items.itemID, creatorData.lastName, creatorData.firstName
		from items, itemCreators, creators, creatorData, creatorTypes
		where
			items.itemID = itemCreators.itemID
			and itemCreators.creatorID = creators.creatorID
			and creators.creatorDataID = creatorData.creatorDataID
			and itemCreators.creatorTypeID = creatorTypes.creatorTypeID
			and creatorTypes.creatorType == "{0}"
		order by itemCreators.orderIndex
		""".format(creator_type)

    def __init__(self, zotero_path, global_variables, noteProvider=None):
        Debuggable.__init__(self, 'libZotero')
        self.gv = global_variables
        self.debug = self.gv.debug

        """
        Intialize zotero.

        Arguments:
        zotero_path		--	A unicode string to the Zotero folder.

        Keyword arguments:
        noteProvider	--	A noteProvider object. (default=None)
        """

        assert (isinstance(zotero_path, unicode))

        self.debug.print_debug(self, u"zotero.__init__(): zotero_path = %s" % zotero_path)

        # Set paths
        self.zotero_path = zotero_path
        self.storage_path = os.path.join(self.zotero_path, u"storage")
        self.zotero_database = os.path.join(self.zotero_path, u"zotero.sqlite")
        self.noteProvider = noteProvider

        if os.name == u"nt":
            home_folder = os.environ[u"USERPROFILE"].decode( \
                sys.getfilesystemencoding())
        elif os.name == u"posix":
            home_folder = os.environ[u"HOME"].decode( \
                sys.getfilesystemencoding())
        else:
            self.debug.print_debug(self, u"zotero.__init__(): you appear to be running an unsupported OS")

        self.gnotero_database = os.path.join(home_folder, u".gnotero.sqlite")

        # Remember search results so results speed up over time
        self.search_cache = {}

        # Check whether verbosity is turned on
        self.verbose = "-v" in sys.argv

        # These dates are treated as special and are not parsed into a year
        # representation
        self.special_dates = u"in press", u"submitted", u"in preparation", \
                             u"unpublished"

        # These extensions are recognized as fulltext attachments
        self.attachment_ext = u".pdf", u".epub"

        self.index = {}
        self.collection_index = []
        self.tag_index = []
        self.last_update = None

        # The notry parameter can be used to show errors which would
        # otherwise be obscured by the try clause
        if "--notry" in sys.argv:
            self.search(u"dummy")

        # Start by updating the database
        try:
            self.search(u"dummy")
            self.error = False
        except Exception as e:
            self.debug.print_debug(self, e)
            self.error = True

    def update(self, force=False):

        """
        Checks if the local copy of the zotero database is up to date. If not,
        the data is also indexed.

        Arguments:
        force		--	Indicates that the data should also be indexed, even
                        if the local copy is up to date. (default=False)
        """

        try:
            stats = os.stat(self.zotero_database)
        except Exception as e:
            self.debug.print_debug(self, u"zotero.update(): %s" % e)
            return False

        # Only update if necessary
        if not force and stats[8] > self.last_update:
            t = time.time()
            self.last_update = stats[8]
            self.index = {}
            self.collection_index = []
            self.search_cache = {}

            # Copy the zotero database to the gnotero copy
            shutil.copyfile(self.zotero_database, self.gnotero_database)
            self.conn = sqlite3.connect(self.gnotero_database)
            self.cur = self.conn.cursor()

            # First create a list of deleted items, so we can ignore those later
            deleted = []
            self.cur.execute(self.deleted_query)
            for item in self.cur.fetchall():
                deleted.append(item[0])

            # Retrieve information about date, publication, volume, issue and
            # title
            self.cur.execute(self.info_query)
            for item in self.cur.fetchall():
                item_id = item[0]
                key = item[3]

                if item_id not in deleted:
                    item_name = item[1]

                    # Parse date fields, because we only want a year or a #
                    # 'special' date
                    if item_name == u"date":
                        item_value = None
                        for sd in self.special_dates:
                            if sd in item[2].lower():
                                item_value = sd
                                break

                        # Dates can have months, days, and years, or just a
                        # year, and can be split by '-' and '/' characters.
                        if item_value is None:
                            # Detect whether the date should be split
                            if u'/' in item[2]:
                                split = u'/'
                            elif u'-' in item[3]:
                                split = u'-'
                            else:
                                split = None
                            # If not, just use the last four characters
                            if split is None:
                                item_value = item[2][-4:]
                            # Else take the first slice that is four characters
                            else:
                                l = item[2].split(split)
                                for i in l:
                                    if len(i) == 4:
                                        item_value = i
                                        break
                    else:
                        item_value = item[2]

                    if item_id not in self.index:
                        self.index[item_id] = zotero_item(item_id, noteProvider=self.noteProvider)
                        self.index[item_id].key = key
                        self.index[item_id].item_type = item[4]

                    if item_name == u"publicationTitle" or item_name == u'bookTitle' or item_name == 'websiteTitle':
                        self.index[item_id].publication = unicode(item_value)
                    elif item_name == u"date":
                        self.index[item_id].date = item_value
                    elif item_name == u"volume":
                        self.index[item_id].volume = item_value
                    elif item_name == u"issue":
                        self.index[item_id].issue = item_value
                    elif item_name == u"title":
                        self.index[item_id].title = unicode(item_value)
                    elif item_name == u"DOI":
                        self.index[item_id].doi = unicode(item_value)
                    elif item_name == u"pages":
                        self.index[item_id].pages = unicode(item_value)
                    elif item_name == u"place":
                        self.index[item_id].place = unicode(item_value)
                    elif item_name == u"publisher":
                        self.index[item_id].publisher = unicode(item_value)
                    elif item_name == u"url":
                        self.index[item_id].url = unicode(item_value)
                    else:
                        self.debug.print_debug(self, u'Unindexed field: {0}'.format(item_name))

            # Retrieve author information
            self.cur.execute(self.creator_query('author'))
            for item in self.cur.fetchall():
                item_id = item[0]
                if item_id not in deleted:
                    # slice tuple as first column is an integer index
                    # next two columns represent lastname and firstname
                    new_authors = item[1:]
                    self.index[item_id].authors.append(new_authors)

            # Retrieve editor information
            self.cur.execute(self.creator_query('editor'))
            for item in self.cur.fetchall():
                item_id = item[0]
                if item_id not in deleted:
                    # slice tuple as first column is an integer index
                    # next two columns represent lastname and firstname
                    new_authors = item[1:]
                    self.index[item_id].editors.append(new_authors)

            # Retrieve translator information
            self.cur.execute(self.creator_query('translator'))
            for item in self.cur.fetchall():
                item_id = item[0]
                if item_id not in deleted:
                    # slice tuple as first column is an integer index
                    # next two columns represent lastname and firstname
                    new_authors = item[1:]
                    self.index[item_id].translators.append(new_authors)

            # Retrieve translator information
            self.cur.execute(self.creator_query('bookAuthor'))
            for item in self.cur.fetchall():
                item_id = item[0]
                if item_id not in deleted:
                    # slice tuple as first column is an integer index
                    # next two columns represent lastname and firstname
                    new_authors = item[1:]
                    self.index[item_id].book_authors.append(new_authors)

            # Retrieve collection information
            self.cur.execute(self.collection_query)
            for item in self.cur.fetchall():
                item_id = item[0]
                if item_id not in deleted:
                    item_collection = item[1]
                    if item_id not in self.index:
                        self.index[item_id] = zotero_item(item_id)
                    self.index[item_id].collections.append(item_collection)
                    if item_collection not in self.collection_index:
                        self.collection_index.append(item_collection)
            # Retrieve tag information
            self.cur.execute(self.tag_query)
            for item in self.cur.fetchall():
                item_id = item[0]
                if item_id not in deleted:
                    item_tag = item[1]
                    if item_id not in self.index:
                        self.index[item_id] = zotero_item(item_id)
                    self.index[item_id].tags.append(item_tag)
                    if item_tag not in self.tag_index:
                        self.tag_index.append(item_tag)
            # Retrieve attachments
            self.cur.execute(self.attachment_query)
            for item in self.cur.fetchall():
                item_id = item[0]
                if item_id not in deleted:
                    if item[1] != None:
                        att = item[1]
                        # If the attachment is stored in the Zotero folder, it is preceded
                        # by "storage:"
                        if att[:8] == u"storage:":
                            item_attachment = att[8:]
                            attachment_id = item[2]
                            if item_attachment[-4:].lower() in \
                                    self.attachment_ext:
                                if item_id not in self.index:
                                    self.index[item_id] = zotero_item(item_id)
                                self.cur.execute( \
                                    u"select items.key from items where itemID = %d" \
                                    % attachment_id)
                                key = self.cur.fetchone()[0]
                                self.index[item_id].fulltext = os.path.join( \
                                    self.storage_path, key, item_attachment)
                        # If the attachment is linked, it is simply the full
                        # path to the attachment
                        else:
                            self.index[item_id].fulltext = att
            self.cur.close()
            self.debug.print_debug(self, u"zotero.update(): indexing completed in %.3fs" % (time.time() - t))

        return True

    def parse_query(self, query):

        """
        Parses a text search query into a list of tuples, which are acceptable
        for zotero_item.match().

        Argument:
        query		--	A search query.

        Returns:
        A list of tuples.
        """

        # Make sure that spaces are handled correctly after
        # semicolons. E.g., Author: Mathot
        while u": " in query:
            query = query.replace(u": ", u":")
        # Parse the terms into a suitable format
        terms = []
        # Check if the criterium is type-specified, like "author: doe"
        import shlex

        for term in query.strip().lower().split():
            s = term.split(u":")
            if len(s) == 2:
                terms.append((s[0].strip(), s[1].strip()))
            else:
                terms.append((None, term.strip()))
        return terms

    def search(self, query):

        """
        Searches the zotero database.

        Argument:
        query		--	A search query.

        Returns:
        A list of zotero_items.
        """

        if not self.update():
            return []
        if query in self.search_cache:
            self.debug.print_debug(self, u"zotero.search(): retrieving results for '%s' from cache" % query)
            return self.search_cache[query]
        t = time.time()
        terms = self.parse_query(query)
        results = []
        for item_id, item in self.index.items():
            if item.match(terms):
                results.append(item)
        self.search_cache[query] = results
        #self.debug.print_debug(self, u"zotero.search(): search for '%s' completed in %.3fs" % (query, time.time() - t))

        return results


def valid_location(path):
    """
    Checks if a given path is a valid Zotero folder, i.e., if it it contains
    zotero.sqlite.

    Arguments:
    path		--	The path to check.

    Returns:
    True if path is a valid Zotero folder, False otherwise.
    """

    assert (isinstance(path, unicode))
    return os.path.exists(os.path.join(path, u"zotero.sqlite"))
