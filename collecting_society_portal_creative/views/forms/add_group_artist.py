# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.creative

import colander
import deform
import logging

from collecting_society_portal.models import WebUser
from collecting_society_portal.views.forms import (
    FormController
)
from ...services import _
from ...models import Artist
from ...resources import ArtistResource

log = logging.getLogger(__name__)


# --- Controller --------------------------------------------------------------

class AddGroupArtist(FormController):
    """
    form controller for creation of artists
    """

    def controller(self):

        self.form = add_group_artist_form(self.request)

        return self.response

    # --- Stages --------------------------------------------------------------

    # --- Conditions ----------------------------------------------------------

    # --- Actions -------------------------------------------------------------


# --- Validators --------------------------------------------------------------

# --- Options -----------------------------------------------------------------

# --- Fields ------------------------------------------------------------------

# --- Schemas -----------------------------------------------------------------

class AddGroupArtistSchema(colander.MappingSchema):
    title = _(u"Add Group Artist")


# --- Forms -------------------------------------------------------------------

def add_group_artist_form(request):
    return deform.Form(
        schema=AddGroupArtistSchema().bind(request=request),
        buttons=[
            deform.Button('submit', _(u"Submit"))
        ]
    )
