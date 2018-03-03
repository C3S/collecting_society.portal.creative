# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal

import logging

from collecting_society_portal.models import (
    Tdb,
    WebUser
)

log = logging.getLogger(__name__)


class Content(Tdb):
    """
    Model wrapper for Tryton model object 'web.user'.
    """

    __name__ = 'content'

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_all(cls):
        """
        Gets all content.

        Returns:
            list (obj[content]): List of content.
            None: if no match is found.
        """
        return cls.get().search([('active', '=', True)])

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_id(cls, uid):
        """
        Searches a content by id.

        Args:
            uid (string): Id of the content.

        Returns:
            obj (content): Content.
            None: If no match is found.
        """
        if uid is None:
            return None
        result = cls.get().search([
            ('active', '=', True),
            ('id', '=', uid)
        ])
        return result[0] if result else None

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_name(cls, name):
        """
        Searches a content by name.

        Args:
            name (str): Name of the content.

        Returns:
            list (content): List of content.
        """
        if name is None:
            return None
        result = cls.get().search([
            ('active', '=', True),
            ('name', '=', name)
        ])
        return result

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_uuid(cls, uuid):
        """
        Searches a content by uuid.

        Args:
            uuid (str): Uuid of the content.

        Returns:
            obj (content): Content.
            None: If no match is found.
        """
        if uuid is None:
            return None
        result = cls.get().search([
            ('active', '=', True),
            ('uuid', '=', uuid)
        ])
        return result[0] if result else None

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_archive(cls, archive):
        """
        Searches a content by archive.

        Args:
            archive (int): Id of the archive.

        Returns:
            list (content): List of content.
        """
        if archive is None:
            return None
        result = cls.get().search([
            ('active', '=', True),
            ('archive', '=', archive)
        ])
        return result

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_party(cls, party_id):
        """
        Searches a content by party id.

        Args:
            party_id (int): Id of the party.

        Returns:
            list (content): List of content.
        """
        if party_id is None:
            return None
        result = cls.get().search([
            ('active', '=', True),
            ('entity_creator', '=', party_id)
        ])
        return result

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_web_user(cls, web_user_id):
        """
        Searches a content by web user id.

        Args:
            web_user_id (int): Id of the user.

        Returns:
            list (content): List of content.
        """
        if web_user_id is None:
            return None
        web_user = WebUser.search_by_id(web_user_id)
        if web_user is None:
            return None
        result = cls.get().search([
            ('active', '=', True),
            ('entity_creator', '=', web_user.party.id)
        ])
        return result

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_creation(cls, creation_id):
        """
        Searches a content by creation id.

        Args:
            creation_id (int): Id of the creation.

        Returns:
            obj (content): Content.
            None: If no match is found.
        """
        if creation_id is None:
            return None
        result = cls.get().search([
            ('active', '=', True),
            ('creation', '=', creation_id)
        ])
        return result[0] if result else None

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_extension(cls, extension):
        """
        Searches a content by extension.

        Args:
            extension (str): Extension of the content.

        Returns:
            list (content): List of content.
        """
        if extension is None:
            return None
        result = cls.get().search([
            ('active', '=', True),
            ('extension', '=', extension)
        ])
        return result

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_mime_type(cls, mime_type):
        """
        Searches a content by mime type.

        Args:
            mime_type (str): Mime type of the content.

        Returns:
            list (content): List of content.
        """
        if mime_type is None:
            return None
        result = cls.get().search([
            ('active', '=', True),
            ('mime_type', '=', mime_type)
        ])
        return result

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_orphans(cls, party_id, category):
        """
        Searches orphan content in category of web user.

        Args:
            request (pyramid.request.Request): Current request.
            party_id (int): Res user id.
            category (str): Category of content.

        Returns:
            list (content): List of content.
            None: If no match is found.
        """
        if party_id is None:
            return None
        result = cls.get().search(
            [
                ('active', '=', True),
                ('entity_creator', '=', party_id),
                ('category', '=', category),
                ('creation', '=', None),
                ('processing_state', '!=', 'rejected')
            ]
        )
        return result or None

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_duplicates_by_user(cls, user_id):
        """
        Searches duplicate content of current user.

        Args:
            request (pyramid.request.Request): Current request.
        Returns:
           list (content): List of content.
           None: If no match is found.
        """
        result = cls.get().search(
            [
                ('active', '=', True),
                ('user', '=', user_id),
                #('duplicate_of', '=', None)
            ]
        )
        return result or None

    @classmethod
    @Tdb.transaction(readonly=True)
    def current_orphans(cls, request, category):
        """
        Searches orphan content in category of current web user.

        Args:
            request (pyramid.request.Request): Current request.
            category (str): Category of content.

        Returns:
            list (content): List of content.
            None: If no match is found.
        """
        party = WebUser.current_web_user(request).party
        return cls.search_orphans(party.id, category)

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_duplicates_by_user(cls, user_id):
        """
        Searches duplicate content of current user.

        Args:
            request (pyramid.request.Request): Current request.
        Returns:
           list (content): List of content.
           None: If no match is found.
        """
        result = cls.get().search(
            [
                ('active', '=', True),
                ('user', '=', user_id),
                #('duplicate_of', '=', None)
            ]
        )
        return result or None


    @classmethod
    @Tdb.transaction(readonly=False)
    def create(cls, vlist):
        """
        Creates content.

        Args:
            vlist (list): List of dictionaries with attributes of a content.
                [
                    {
                        'active': bool,
                        'uuid': str (required),
                        'name': str (required),
                        'size': int,
                        'path': str,
                        'preview_path': str,
                        'mime_type': str,
                        'mediation': bool,
                        'duplicate_of': int,
                        'duplicates': list,
                        'entity_origin': str (required),
                        'entity_creator': str (required),
                        'user_committed_state': bool,
                        'fingerprintlogs': list,
                        'checksums': list,
                        'archive': int,
                        'category': str (required),
                        'creation': int,
                        'processing_state': str,
                        'processing_hostname': str,
                        'rejection_reason': str,
                        'length': float,
                        'channels': int,
                        'sample_rate': int,
                        'sample_width': int
                    },
                    {
                        ...
                    }
                ]

        Returns:
            list (obj[content]): List of created content.
            None: If no object was created.

        Raises:
            KeyError: If required field is missing.
        """
        for values in vlist:
            if 'processing_state' not in values:
                raise KeyError('processing_state is missing')
            if 'name' not in values:
                raise KeyError('name is missing')
            if 'uuid' not in values:
                raise KeyError('uuid is missing')
            if 'entity_origin' not in values:
                raise KeyError('entity_origin is missing')
            if 'entity_creator' not in values:
                raise KeyError('entity_creator is missing')
            if 'category' not in values:
                raise KeyError('category is missing')
        log.debug('create content:\n{}'.format(vlist))
        result = cls.get().create(vlist)
        return result or None
