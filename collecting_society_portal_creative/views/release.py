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
from ..resources import ReleaseResource

log = logging.getLogger(__name__)


@view_defaults(
    context='..resources.ReleaseResource',
    permission='read')
class ReleaseViews(ViewBase):

    @view_config(
        name='')
    def root(self):
        return self.redirect(ReleaseResource, 'list')

    @view_config(
        name='list',
        renderer='../templates/release/list.pt',
        decorator=Tdb.transaction(readonly=True))
    def list(self):
        web_user = WebUser.current_web_user(self.request)
        _party_id = web_user.party.id
        return {
            'releases': {}
        }
