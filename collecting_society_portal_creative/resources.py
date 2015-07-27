# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.creative

import logging

from collecting_society_portal.services import _
from collecting_society_portal.resources import (
    ResourceBase,
    FrontendResource,
    BackendResource
)

log = logging.getLogger(__name__)


def include_web_resources(config):
    pass


class ArtistResource(ResourceBase):
    __name__ = "artists"
    __parent__ = None
    __children__ = {}
    __registry__ = {}
    __acl__ = []


class AddArtistResource(ResourceBase):
    __name__ = "add"
    __parent__ = None
    __children__ = {}
    __registry__ = {}
    __acl__ = []


class CreationResource(ResourceBase):
    __name__ = "creations"
    __parent__ = None
    __children__ = {}
    __registry__ = {}
    __acl__ = []
