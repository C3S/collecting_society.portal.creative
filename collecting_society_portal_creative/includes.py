# For copyright and license terms, see COPYRIGHT.rst (top level of repository)
# Repository: https://github.com/C3S/collecting_society.portal.creative

"""
Functions to include resources/views and register content by the plugin system.

The following functions are called by convention on app creation:

- web_resources
- web_registry
- web_views
- api_views
"""


def web_resources(config):
    '''
    Extends the resource tree for the web service.

    Note:
        The function is called by the plugin system, when the app is created.

    Args:
        config (pyramid.config.Configurator): App config

    Returns:
        None
    '''
    pass


def web_registry(config):
    '''
    Extends the registry for content elements for the web service.

    Note:
        The function is called by the plugin system, when the app is created.

    Args:
        config (pyramid.config.Configurator): App config

    Returns:
        None
    '''
    pass


def web_views(config):
    '''
    Adds the views for the web service.

    Note:
        The function is called by the plugin system, when the app is created.

    Args:
        config (pyramid.config.Configurator): App config

    Returns:
        None
    '''
    config.add_static_view('static/creative', 'static', cache_max_age=3600)
    config.scan(ignore='.views.api')


def api_views(config):
    '''
    Adds the views for the api service.

    Note:
        The function is called by the plugin system, when the app is created.

    Args:
        config (pyramid.config.Configurator): App config

    Returns:
        None
    '''
    settings = config.get_settings()

    # views
    if settings['env'] == 'development':
        config.add_static_view('static/creative', 'static', cache_max_age=3600)
    config.scan('.views.api')
