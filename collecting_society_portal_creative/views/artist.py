# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.creative

import logging

from pyramid.view import (
    view_config,
    view_defaults
)

from collecting_society_portal.models import (
    Tdb,
    WebUser
)
from collecting_society_portal.views import ViewBase
from ..models import (
    Artist,
    Creation
)
from ..services import _
from ..resources import (
    SoloArtistResource,
    GroupArtistResource
)
from .forms import (
    AddSoloArtist,
    AddGroupArtist
)

log = logging.getLogger(__name__)


@view_defaults(
    context='..resources.ArtistResource',
    permission='read')
class ArtistViews(ViewBase):

    @view_config(
        name='')
    def root(self):
        return self.redirect(SoloArtistResource, 'list')


@view_defaults(
    context='..resources.SoloArtistResource',
    permission='read')
class SoloArtistViews(ViewBase):

    @view_config(
        name='')
    def root(self):
        return self.redirect(SoloArtistResource, 'list')

    @view_config(
        name='list',
        renderer='../templates/artist/list.pt',
        decorator=Tdb.transaction(readonly=True))
    def list(self):
        web_user = WebUser.current_web_user(self.request)
        _party_id = web_user.party.id
        return {
            'artists': Artist.search_solo_artists_by_party(_party_id)
        }

    @view_config(
        name='show',
        renderer='../templates/artist/show.pt',
        decorator=Tdb.transaction(readonly=True))
    def show(self):
        artist_id = self.request.subpath[-1]
        _artist = Artist.search_by_id(artist_id)
        _creations = Creation.search_by_artist(artist_id)
        _contributions = Creation.search_by_contributions_of_artist(artist_id)
        return {
            'artist': _artist,
            'creations': _creations,
            'contributions': _contributions
        }

    @view_config(
        name='add',
        renderer='../templates/artist/add_solo.pt')
    def add_solo_artist(self):
        self.register_form(AddSoloArtist)
        return self.process_forms()

    @view_config(
        name='delete',
        decorator=Tdb.transaction(readonly=False))
    def delete_artist(self):
        email = self.request.unauthenticated_userid

        _id = self.request.subpath[0]
        if _id is None:
            self.request.session.flash(
                _(u"Could not delete artist - id is missing"),
                'main-alert-warning'
            )
            return self.redirect(SoloArtistResource, 'list')

        artist = Artist.search_by_id(_id)
        if artist is None:
            self.request.session.flash(
                _(u"Could not delete artist - artist not found"),
                'main-alert-warning'
            )
            return self.redirect(SoloArtistResource, 'list')

        _name, _code = artist.name, artist.code
        Artist.delete([artist])
        log.info("artist delete successful for %s: %s (%s)" % (
            email, _name, _code
        ))
        self.request.session.flash(
            _(u"Artist deleted: ") + _name + ' (' + _code + ')',
            'main-alert-success'
        )
        return self.redirect(SoloArtistResource, 'list')


@view_defaults(
    context='..resources.GroupArtistResource',
    permission='read')
class GroupArtistViews(ViewBase):

    @view_config(
        name='')
    def root(self):
        return self.redirect(GroupArtistResource, 'list')

    @view_config(
        name='list',
        renderer='../templates/artist/list.pt',
        decorator=Tdb.transaction(readonly=True))
    def list(self):
        web_user = WebUser.current_web_user(self.request)
        _party_id = web_user.party.id
        return {
            'artists': Artist.search_group_artists_by_party(_party_id)
        }

    @view_config(
        name='show',
        renderer='../templates/artist/show.pt',
        decorator=Tdb.transaction(readonly=True))
    def show(self):
        artist_id = self.request.subpath[-1]
        _artist = Artist.search_by_id(artist_id)
        _creations = Creation.search_by_artist(artist_id)
        _contributions = Creation.search_by_contributions_of_artist(artist_id)
        return {
            'artist': _artist,
            'creations': _creations,
            'contributions': _contributions
        }

    @view_config(
        name='add',
        renderer='../templates/artist/add_group.pt')
    def add(self):
        self.register_form(AddGroupArtist)
        return self.process_forms()

    @view_config(
        name='delete',
        decorator=Tdb.transaction(readonly=False))
    def delete_artist(self):
        email = self.request.unauthenticated_userid

        _id = self.request.subpath[0]
        if _id is None:
            self.request.session.flash(
                _(u"Could not delete artist - id is missing"),
                'main-alert-warning'
            )
            return self.redirect(GroupArtistResource, 'list')

        artist = Artist.search_by_id(_id)
        if artist is None:
            self.request.session.flash(
                _(u"Could not delete artist - artist not found"),
                'main-alert-warning'
            )
            return self.redirect(GroupArtistResource, 'list')

        _name, _code = artist.name, artist.code
        Artist.delete([artist])
        log.info("artist delete successful for %s: %s (%s)" % (
            email, _name, _code
        ))
        self.request.session.flash(
            _(u"Artist deleted: ") + _name + ' (' + _code + ')',
            'main-alert-success'
        )
        return self.redirect(GroupArtistResource, 'list')
