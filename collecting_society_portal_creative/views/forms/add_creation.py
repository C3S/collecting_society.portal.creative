# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.creative

import colander
import deform
import logging

from collecting_society_portal.models import (
    Tdb,
    WebUser
)
from collecting_society_portal.views.forms import (
    FormController,
    deferred_file_upload_widget
)
from ...services import _
from ...models import (
    Artist,
    Creation,
    License
)
from ...resources import CreationResource

log = logging.getLogger(__name__)


# --- Controller --------------------------------------------------------------

class AddCreation(FormController):
    """
    form controller for creation of creations
    """

    __stage__ = 'upload_audiofile'  # initial stage

    def controller(self):

        # upload of creation file
        if self.stage == 'upload_audiofile':
            self.upload_audiofile()

        # add metadata to creation
        if self.stage == 'add_metadata':
            self.add_metadata()

        # add contributions to creation
        if self.stage == 'add_contributions':
            self.add_contributions()

        # add licenses to creation
        if self.stage == 'add_licenses':
            self.add_licenses()

        # add relations to other creations to creation
        if self.stage == 'add_creation_relations':
            self.add_creation_relations()

        log.debug(
            (
                "self.stage: %s\n"
                "self.appstruct: %s\n"
                "self.data: %s\n"
            ) % (
                self.stage,
                self.appstruct,
                self.data
            )
        )

        return self.response

    # --- Stages --------------------------------------------------------------

    def upload_audiofile(self):
        self.form = upload_audiofile_form(self.request)
        self.render(self.data)

        if self.submitted('add_metadata') and self.validate():
            self.data.update(self.appstruct.copy())
            self.stage = 'add_metadata'
            self.add_metadata()

    def add_metadata(self):
        self.form = add_metadata_form(self.request)
        self.render(self.data)

        if self.submitted('upload_audiofile'):
            self.stage = 'upload_audiofile'
            self.upload_audiofile()

        if self.submitted('add_contributions') and self.validate():
            self.data.update(self.appstruct.copy())
            self.stage = 'add_contributions'
            self.add_contributions()

    def add_contributions(self):
        self.form = add_contributions_form(self.request)
        self.render(self.data)

        if self.submitted('add_metadata'):
            self.stage = 'add_metadata'
            self.add_metadata()
            self.render(self.data)

        if self.submitted('add_licenses') and self.validate():
            self.data.update(self.appstruct.copy())
            self.stage = 'add_licenses'
            self.add_licenses()

    def add_licenses(self):
        self.form = add_licenses_form()
        self.render(self.data)

        if self.submitted('add_contributions'):
            self.stage = 'add_contributions'
            self.add_contributions()
            self.render(self.data)

        if self.submitted('add_creation_relations') and self.validate():
            self.data.update(self.appstruct.copy())
            self.stage = 'add_creation_relations'
            self.add_creation_relations()

    def add_creation_relations(self):
        self.form = add_creation_relations_form(self.request)
        self.render(self.data)

        if self.submitted('add_licenses'):
            self.stage = 'add_licenses'
            self.add_licenses()
            self.render(self.data)

        if self.submitted('save_creation') and self.validate():
            self.data.update(self.appstruct.copy())
            self.stage = 'save_creation'
            self.save_creation()

    # --- Conditions ----------------------------------------------------------

    # --- Actions -------------------------------------------------------------

    @Tdb.transaction(readonly=False)
    def save_creation(self):
        email = self.request.unauthenticated_userid

        _creation = {
            'title': self.data['title'],
            'artist': self.data['artist'],
        }
        if self.data['contributions']:
            _creation['contributions'] = []
            for contribution in self.data['contributions']:
                _creation['contributions'].append(
                    (
                        'create',
                        [{
                            'type': contribution['type'],
                            'artist': contribution['artist']
                        }]
                    )
                )
        if self.data['licenses']:
            _creation['licenses'] = []
            for license_id in self.data['licenses']:
                _creation['licenses'].append(
                    (
                        'create',
                        [{
                            'license': license_id
                        }]
                    )
                )
        if self.data['original_creations']:
            _creation['original_relations'] = []
            for original_creation in self.data['original_creations']:
                _creation['original_relations'].append(
                    (
                        'create',
                        [{
                            'original_creation': original_creation['creation'],
                            'allocation_type': original_creation['type']
                        }]
                    )
                )
        if self.data['derivative_creations']:
            _creation['derivative_relations'] = []
            for derivative_creation in self.data['derivative_creations']:
                _creation['derivative_relations'].append(
                    (
                        'create',
                        [{
                            'derivative_creation': derivative_creation[
                                'creation'
                            ],
                            'allocation_type': derivative_creation['type']
                        }]
                    )
                )

        for derivative_creation in self.data['derivative_creations']:
            derivative_creation['creation']
            derivative_creation['type']

        creations = Creation.create([_creation])
        if not creations:
            log.info("creation add failed for %s: %s" % (email, _creation))
            self.request.session.flash(
                _(u"Creation could not be added: ") + _creation['title'],
                'main-alert-danger'
            )
            self.redirect(CreationResource, 'list')
            return
        creation = creations[0]

        Attachment = Tdb.get('ir.attachment')
        attachment = Attachment(
            type='data',
            name=self.data['audiofile']['filename'],
            resource=creation,
            data=self.data['audiofile']['fp'].read()
        )
        attachment.save()

        log.info("creation add successful for %s: %s" % (email, creation))
        self.request.session.flash(
            _(u"Creation added: ")+creation.title+" ("+creation.code+")",
            'main-alert-success'
        )
        self.remove()
        self.clean()
        self.redirect(CreationResource, 'list')


# --- Validators --------------------------------------------------------------

# --- Options -----------------------------------------------------------------

artist_relation_options = (
    ('', _(u"- Select -")),
    ('performance', _(u"Performance")),
    ('composition', _(u"Composition")),
    ('text', _(u"Text"))
)

creation_relation_options = (
    ('', _(u"- Select -")),
    ('adaption', _(u"Adaption")),
    ('cover', _(u"Cover")),
    ('remix', _(u"Remix"))
)


@Tdb.transaction(readonly=True)
def licenses_options():
    licenses = License.search_all()
    return [(license.id, license.name) for license in licenses]


# --- Fields ------------------------------------------------------------------

@colander.deferred
def current_artists_select_widget(node, kw):
    request = kw.get('request')
    web_user = WebUser.current_web_user(request)
    artists = Artist.search_by_party(web_user.party.id)
    artist_options = [(artist.id, artist.name) for artist in artists]
    widget = deform.widget.Select2Widget(values=artist_options)
    return widget


@colander.deferred
def solo_artists_select_widget(node, kw):
    solo_artists = Artist.search_all_solo_artists()
    solo_artist_options = [(artist.id, artist.name) for artist in solo_artists]
    widget = deform.widget.Select2Widget(values=solo_artist_options)
    return widget


@colander.deferred
def creations_select_widget(node, kw):
    creations = Creation.search_all()
    creations_options = [
        (creation.id, creation.title + ' (' + creation.artist.name + ')')
        for creation in creations
    ]
    widget = deform.widget.Select2Widget(values=creations_options)
    return widget


class AudiofileField(colander.SchemaNode):
    oid = "audiofile"
    schema_type = deform.FileData
    widget = deferred_file_upload_widget


class TitleField(colander.SchemaNode):
    oid = "title"
    schema_type = colander.String


class SoloArtistField(colander.SchemaNode):
    oid = "artist"
    schema_type = colander.Integer
    widget = solo_artists_select_widget


class CurrentArtistField(colander.SchemaNode):
    oid = "artist"
    schema_type = colander.Integer
    widget = current_artists_select_widget


class ContributionTypeField(colander.SchemaNode):
    schema_type = colander.String
    widget = deform.widget.SelectWidget(
        values=artist_relation_options
    )


class LicensesField(colander.SchemaNode):
    oid = "licenses"
    schema_type = colander.Set
    widget = deform.widget.Select2Widget(
        values=licenses_options(),
        multiple=True
    )


class CreationField(colander.SchemaNode):
    oid = "creation"
    schema_type = colander.Integer
    widget = creations_select_widget


class RelationTypeField(colander.SchemaNode):
    schema_type = colander.String
    widget = deform.widget.SelectWidget(
        values=creation_relation_options
    )


class CollectingSocietyField(colander.SchemaNode):
    oid = "collecting-society"
    schema_type = colander.String
    missing = ""


class NeighbouringRightsField(colander.SchemaNode):
    oid = "neighbouring-rights"
    schema_type = colander.Bool
    widget = deform.widget.CheckboxWidget()
    missing = ""


class NeighbouringRightsSocietyField(colander.SchemaNode):
    oid = "neighbouring-rights-society"
    schema_type = colander.String
    missing = ""


class LabelNameField(colander.SchemaNode):
    oid = "label-name"
    schema_type = colander.String
    missing = ""


class LabelCodeField(colander.SchemaNode):
    oid = "label-code"
    schema_type = colander.String
    missing = ""


class LabelOrderNumberField(colander.SchemaNode):
    oid = "label-order-number"
    schema_type = colander.Integer
    missing = ""


class LabelUrlField(colander.SchemaNode):
    oid = "label-url"
    schema_type = colander.String
    missing = ""


class EanUpcField(colander.SchemaNode):
    oid = "ean-upc"
    schema_type = colander.Integer
    missing = ""


class IsrcField(colander.SchemaNode):
    oid = "isrc"
    schema_type = colander.String
    missing = ""


class ReleaseDateField(colander.SchemaNode):
    oid = "release-date"
    schema_type = colander.DateTime
    missing = ""


class ReleaseCancellationDateField(colander.SchemaNode):
    oid = "release-cancellation-date"
    schema_type = colander.DateTime
    missing = ""


class OnlineReleaseDateField(colander.SchemaNode):
    oid = "online-release-date"
    schema_type = colander.DateTime
    missing = ""


class OnlineReleaseCancellationDateField(colander.SchemaNode):
    oid = "online-release-cancellation-date"
    schema_type = colander.DateTime
    missing = ""


# --- Schemas -----------------------------------------------------------------

class UploadAudiofileSchema(colander.MappingSchema):
    title = _(u"Upload audiofile")
    audiofile = AudiofileField(
        title=_(u"Upload Audiofile")
    )


class AddMetadataSchema(colander.MappingSchema):
    title = _(u"Add metadata")
    creation_title = TitleField(
        name='title',
        title=_(u"Title")
    )
    artist = CurrentArtistField(
        title=_(u"Featured Artist")
    )
    collecting_society = CollectingSocietyField()
    neighbouring_rights = NeighbouringRightsField()
    neighbouring_rights_society = NeighbouringRightsSocietyField()
    label_name = LabelNameField()
    label_code = LabelCodeField()
    label_order_number = LabelOrderNumberField()
    label_url = LabelUrlField()
    ean_upc = EanUpcField()
    isrc = IsrcField()
    release_date = ReleaseDateField()
    release_cancellation_date = ReleaseCancellationDateField()
    online_release_date = OnlineReleaseDateField()
    online_release_cancellation_date = OnlineReleaseCancellationDateField()


class ArtistRelationSchema(colander.Schema):
    artist = SoloArtistField(
        title=_(u"Solo artist")
    )
    type = ContributionTypeField(
        title=_(u"Type")
    )


class ArtistRelationSequence(colander.SequenceSchema):
    contribution = ArtistRelationSchema()


class AddContributionsSchema(colander.MappingSchema):
    title = _(u"Add contributions")
    contributions = ArtistRelationSequence(
        title=_(u"Contributions")
    )


class AddLicencesSchema(colander.MappingSchema):
    title = _(u"Add licences")
    licenses = LicensesField(
        title=_(u"Licenses")
    )


class CreationRelationSchema(colander.Schema):
    creation = CreationField(
        title=_(u"Artist")
    )
    type = RelationTypeField(
        title=_(u"Type")
    )


class CreationRelationSequence(colander.SequenceSchema):
    contribution = CreationRelationSchema()


class AddCreationRelationsSchema(colander.MappingSchema):
    title = _(u"Add relations to other creations")
    original_creations = CreationRelationSequence(
        title=_(u"Original creations")
    )
    derivative_creations = CreationRelationSequence(
        title=_(u"Derivative creations")
    )


# --- Forms -------------------------------------------------------------------

def upload_audiofile_form(request):
    return deform.Form(
        schema=UploadAudiofileSchema().bind(request=request),
        buttons=[
            deform.Button('add_metadata', _(u"Continue to metadata"))
        ]
    )


def add_metadata_form(request):
    return deform.Form(
        schema=AddMetadataSchema().bind(request=request),
        buttons=[
            deform.Button(
                'add_contributions', _(u"Continue to contributions")
            ),
            deform.Button('upload_audiofile', _(u"Back to audiofile"))
        ]
    )


def add_contributions_form(request):
    return deform.Form(
        schema=AddContributionsSchema().bind(request=request),
        buttons=[
            deform.Button('add_licenses', _(u"Continue to licences")),
            deform.Button('add_metadata', _(u"Back to metadata"))
        ]
    )


def add_licenses_form():
    return deform.Form(
        schema=AddLicencesSchema(),
        buttons=[
            deform.Button(
                'add_creation_relations', _(u"Continue to relations")
            ),
            deform.Button('add_contributions', _(u"Back to contributions"))
        ]
    )


def add_creation_relations_form(request):
    return deform.Form(
        schema=AddCreationRelationsSchema().bind(request=request),
        buttons=[
            deform.Button('save_creation', _(u"Save creation")),
            deform.Button('add_licenses', _(u"Back to licences"))
        ]
    )
