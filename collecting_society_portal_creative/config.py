# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.creative


def include_web_views(config):
    config.add_static_view('static/creative', 'static', cache_max_age=3600)
    config.scan(ignore='.views.api')


def include_api_views(config):
    settings = config.get_settings()

    # views
    if settings['env'] == 'development':
        config.add_static_view('static/creative', 'static', cache_max_age=3600)
    config.scan('.views.api')
