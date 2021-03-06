# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.creative

import colander
import deform
import logging

from collecting_society_portal.services import iban
from collecting_society_portal.models import (
    Tdb,
    WebUser,
    BankAccountNumber
)
from collecting_society_portal.views.forms import (
    FormController,
    deferred_file_upload_widget
)
from ...services import _
from ...models import Artist
from ...resources import ArtistResource

log = logging.getLogger(__name__)


# --- Controller --------------------------------------------------------------

class AddSoloArtist(FormController):
    """
    form controller for creation of artists
    """

    def controller(self):

        self.form = add_solo_artist_form(self.request)

        if self.submitted() and self.validate():
            self.create_artist()

        return self.response

    # --- Stages --------------------------------------------------------------

    # --- Conditions ----------------------------------------------------------

    # --- Actions -------------------------------------------------------------

    @Tdb.transaction(readonly=False)
    def create_artist(self):
        email = self.request.unauthenticated_userid
        party = WebUser.current_party(self.request)

        _artist = {
            'party': party,
            'group': False,
            'name': self.appstruct['artist']['name'],
            'description': self.appstruct['artist']['description'] or ''
        }
        if self.appstruct['artist']['picture']:
            picture_data = self.appstruct['artist']['picture']['fp'].read()
            mimetype = self.appstruct['artist']['picture']['mimetype']
            _artist['picture_data'] = picture_data
            _artist['picture_data_mime_type'] = mimetype

        artists = Artist.create([_artist])

        if not artists:
            log.info("artist add failed for %s: %s" % (email, _artist))
            self.request.session.flash(
                _(u"Artist could not be added: ") + _artist['name'],
                'main-alert-danger'
            )
            self.redirect(ArtistResource, 'list')
            return
        artist = artists[0]

        if self.appstruct['bank_account']['type']:
            _bank_account_number = {
                'bic': self.appstruct['bank_account']['bic'],
                'type': self.appstruct['bank_account']['type'],
            }
            if self.appstruct['bank_account']['type'] == 'iban':
                number = self.appstruct['bank_account']['number']
                _bank_account_number['number'] = number
            bank_account_number = BankAccountNumber.create(
                artist.party, [_bank_account_number]
            )[0]
            artist.bank_account_number = bank_account_number
            artist.save()

        log.info("artist add successful for %s: %s" % (email, artist))
        self.request.session.flash(
            _(u"Artist added: ") + artist.name + " (" + artist.code + ")",
            'main-alert-success'
        )

        self.redirect(ArtistResource, 'list')


# --- Validators --------------------------------------------------------------

def bank_account_is_complete(node, values):
    if values['type'] or values['number'] or values['bic']:
        exc = colander.Invalid(node)
        if not values['type']:
            exc['type'] = _(u"Type missing")
        if not values['number']:
            exc['number'] = _(u"Number missing")
        if not values['bic']:
            exc['bic'] = _(u"BIC missing")
        if exc.children:
            raise exc


def bank_account_number_is_valid(node, values):
    if values['type'] == 'iban':
        try:
            number = values['number'].replace(" ", "")
            code, checksum, bank, account = iban.check_iban(number)
        except iban.IBANError:
            exc = colander.Invalid(node)
            exc['number'] = _(u"Number is not a correct IBAN")
            raise exc


def bank_account_number_is_unique(value):
    if not BankAccountNumber.search_by_number(value):
        return True
    return "Number already exists"


# --- Options -----------------------------------------------------------------

type_options = (
    ('', ''),
    ('iban', 'IBAN')
)


# --- Fields ------------------------------------------------------------------

class NameField(colander.SchemaNode):
    oid = "name"
    schema_type = colander.String


class DescriptionField(colander.SchemaNode):
    oid = "description"
    schema_type = colander.String
    widget = deform.widget.TextAreaWidget()
    missing = ""


class PictureField(colander.SchemaNode):
    oid = "picture"
    schema_type = deform.FileData
    widget = deferred_file_upload_widget
    missing = ""


class TypeField(colander.SchemaNode):
    oid = "type"
    schema_type = colander.String
    widget = deform.widget.SelectWidget(values=type_options)
    missing = ""


class NumberField(colander.SchemaNode):
    oid = "number"
    schema_type = colander.String
    validator = colander.Function(bank_account_number_is_unique)
    missing = ""


class BicField(colander.SchemaNode):
    oid = "bic"
    schema_type = colander.String
    missing = ""


# --- Schemas -----------------------------------------------------------------

class SoloArtistSchema(colander.MappingSchema):
    title = _(u"Artist")
    name = NameField(
        title=_(u"Name")
    )
    description = DescriptionField(
        title=_(u"Description")
    )
    picture = PictureField(
        title=_(u"Picture")
    )


class BankAccountNumberSchema(colander.MappingSchema):
    title = _(u"Bank Account")
    bic = BicField(
        title=_(u"BIC")
    )
    type = TypeField(
        title=_(u"Type")
    )
    number = NumberField(
        title=_(u"Number")
    )
    validator = colander.All(
        bank_account_is_complete,
        bank_account_number_is_valid
    )


class AddSoloArtistSchema(colander.MappingSchema):
    title = _(u"Add Solo Artist")
    artist = SoloArtistSchema()
    bank_account = BankAccountNumberSchema()


# --- Forms -------------------------------------------------------------------

def add_solo_artist_form(request):
    return deform.Form(
        schema=AddSoloArtistSchema().bind(request=request),
        buttons=[
            deform.Button('submit', _(u"Submit"))
        ]
    )
