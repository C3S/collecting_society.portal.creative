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
        return cls.get().search([])

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
        result = cls.get().search([('id', '=', uid)])
        return result[0] if result else None

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_name(cls, name):
        """
        Searches a content by name.

        Args:
            name (str): Name of the content.

        Returns:
            obj (content): Content.
            None: If no match is found.
        """
        if name is None:
            return None
        result = cls.get().search([('name', '=', name)])
        return result[0] if result else None

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_user(cls, user_id):
        """
        Searches a content by user id.

        Args:
            user_id (int): Id of the user.

        Returns:
            obj (content): Content.
            None: If no match is found.
        """
        if user_id is None:
            return None
        result = cls.get().search([('user', '=', user_id)])
        return result[0] if result else None

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_web_user(cls, web_user_id):
        """
        Searches a content by web user id.

        Args:
            web_user_id (int): Id of the user.

        Returns:
            obj (content): Content.
            None: If no match is found.
        """
        if web_user_id is None:
            return None
        web_user = WebUser.search_by_id(web_user_id)
        if web_user is None:
            return None
        result = cls.get().search([('user', '=', web_user.user.id)])
        return result[0] if result else None

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
        result = cls.get().search([('creation', '=', creation_id)])
        return result[0] if result else None

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_extension(cls, extension):
        """
        Searches a content by extension.

        Args:
            extension (str): Extension of the content.

        Returns:
            obj (content): Content.
            None: If no match is found.
        """
        if extension is None:
            return None
        result = cls.get().search([('extension', '=', extension)])
        return result[0] if result else None

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_by_mime_type(cls, mime_type):
        """
        Searches a content by mime type.

        Args:
            mime_type (str): Mime type of the content.

        Returns:
            obj (content): Content.
            None: If no match is found.
        """
        if mime_type is None:
            return None
        result = cls.get().search([('mime_type', '=', mime_type)])
        return result[0] if result else None

    @classmethod
    @Tdb.transaction(readonly=True)
    def search_orphans(cls, web_user_id, category):
        """
        Searches orphan content in category of web user.

        Args:
            request (pyramid.request.Request): Current request.
            category (str): Category of content.

        Returns:
            list (content): List of content.
            None: If no match is found.
        """
        if web_user_id is None:
            return None
        result = cls.get().search(
            [
                ('user', '=', web_user_id),
                ('category', '=', category),
                ('creation', '=', None)
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
        web_user = WebUser.current_web_user(request)
        return cls.search_orphans(web_user.id, category)

    @classmethod
    @Tdb.transaction(readonly=False)
    def create(cls, vlist):
        """
        Creates content.

        Args:
            vlist (list): List of dictionaries with attributes of a content.
                [
                    {
                        'name': str (required),
                        'category': str (required),
                        'creation': int,
                        'user': int,
                        'mime_type': str,
                        'length': float,
                        'channels': int,
                        'sample_rate': int,
                        'sample_width': int,
                        'size': int,
                        'path': str,
                        'preview_path': str,
                        'archive': str
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
            if 'name' not in values:
                raise KeyError('name is missing')
            if 'category' not in values:
                raise KeyError('category is missing')
        log.debug('create content:\n{}'.format(vlist))
        result = cls.get().create(vlist)
        return result or None
