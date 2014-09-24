__all__ = [ 'general', 'users', 'samples' ] 

from aleph.webui import babel, app
from aleph.utils import from_iso8601, humansize
from flask import request, g
from aleph.webui.utils import geoip

@babel.localeselector
def get_locale():

    user = getattr(g, 'user', None)
    if user is not None and hasattr(user, 'locale'):
        if '-' in user.locale:
            return user.locale.split('-')[0]
        else:
            return user.locale

    locale = request.accept_languages.best_match(app.config.get('LANGUAGES').keys())

    if '-' in locale:
        return locale.split('-')[0]

    return locale

@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None and hasattr(user, 'timezone'):
        return user.timezone

    # Try to guess by Geo IP
    geo = geoip()
    tz = geo.time_zone_by_addr(request.remote_addr)
    if tz:
        return tz

# Custom Filters
def filter_strtoutc(value):
    return from_iso8601(value)

app.jinja_env.filters['str2utc'] = filter_strtoutc
app.jinja_env.filters['humansize'] = humansize
