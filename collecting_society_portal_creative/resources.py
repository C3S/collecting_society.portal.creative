# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.creative

from collecting_society_portal.resources import ResourceBase


class ArtistResource(ResourceBase):
    __name__ = "artists"
    __parent__ = None
    __children__ = {}
    __registry__ = {}
    __acl__ = []


class ReleaseResource(ResourceBase):
    __name__ = "releases"
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
