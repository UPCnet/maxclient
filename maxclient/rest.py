from client import MaxClient as RPCMaxClient
from functools import partial
from hashlib import sha1
from resources import RESOURCES as ROUTES

import json
import re
import requests

DEFAULT_MAX_SERVER = 'http://localhost:8081'
DEFAULT_OAUTH_SERVER = 'https://oauth.upcnet.es'
DEFAULT_SCOPE = 'widgetcli'
DEFAULT_GRANT_TYPE = 'password'
DEFAULT_CLIENT_ID = 'MAX'


class ResourceVariableWrappers(object):
    """
        Container to all the defined variable wrappers
    """
    def _hash_(self, value):
        """
            Adapter to {hash} variable
            Transforms any value into a hash, if it's not already a hash.
        """
        if re.match(r'^[0-9a-f]{40}$', value):
            return value
        else:
            return sha1(value).hexdigest()


class RequestError(Exception):
    """
    """


class Resource(object):
    """
    """

    def __init__(self, parent, attr):
        self.client = parent.client
        self.parent = parent
        self._name = attr
        self.routes = parent.routes[attr]

    @property
    def path(self):
        return '/'.join([self.parent.path, self._name])

    @property
    def uri(self):
        return self.client.url + self.path

    def __getattr__(self, attr):
        """
            Returns a ResourceCollection  if the accessed attribute mathes
            a valid point in the current routes map
        """
        if attr in self.routes.keys():
            return ResourceCollection(self, attr)
        elif attr in ['get', 'post', 'put', 'delete', 'head']:
            return partial(self.client._make_request_, self, attr)
        return AttributeError("Resource not found {}".format(attr))


class ResourceCollection(Resource):
    """
    """

    def __repr__(self):
        return '<Lazy Resource Collection @ "{}">'.format(self.path)

    def __getitem__(self, key):
        """
            Returns a ResourceItem representing a Item on the collection
        """

        return ResourceItem(self, key)


class ResourceItem(Resource):
    """
    """

    wrappers = ResourceVariableWrappers()

    def __init__(self, parent, attr):
        self.parent = parent
        self.client = parent.client
        self.rest_param = self.get_rest_param()
        self._name = self.parse_rest_param(attr)
        self.routes = parent.routes[self.rest_param]

    def parse_rest_param(self, value):
        """
            Transparently adapt values based on variable definitions
            return raw value if no adapation defined for variable
        """
        wrapper_method_name = re.sub(r'{(.*?)}', r'_\1_', self.rest_param)
        wrapper_method = getattr(self.wrappers, wrapper_method_name, None)
        if wrapper_method_name is None:
            return value
        else:
            return wrapper_method(value)

    def get_rest_param(self):
        """
            Searches for variable wrappers {varname} in the current level routes.
            There should be only one available {varname} for each level, so first one is
            returned, otherwise an exception is raised.
        """
        resource_wrappers = [a for a in self.parent.routes.keys() if re.match(r'{.*?}', a)]
        if resource_wrappers:
            if len(resource_wrappers) != 1:
                raise KeyError("Resource collection {} has more than one wrapper defined".format(self.parent.path))
            return resource_wrappers[0]
        raise KeyError("<Resource Item {}".format(self.parent.path))

    def __repr__(self):
        return '<Lazy Resource Item @ {}>'.format(self.path)


class MaxClient(RPCMaxClient):

    path = ''

    def _make_request_(self, resource, method_name, data=None, **kwargs):
        """
            Prepare call parameters  based on method_name, and
            make the appropiate call using requests.
            Responses with an error will raise an exception
        """

        # User has provided us the constructed query
        if isinstance(data, list) or isinstance(data, dict):
            query = data
        # Otherwise construct it from kwargs
        else:
            query = dict(kwargs)

        # Construct uri with optional query string
        uri = resource.uri
        if 'qs' in kwargs:
            uri = '{}?{}'.format(uri, kwargs['qs'])
            del kwargs['qs']

        # Set default requests parameters
        headers = {'content-type': 'application/json'}
        headers.update(self.client.OAuth2AuthHeaders())
        method_kwargs = {
            'headers': headers,
            'verify': False
        }

        # Add query to body only in this methods
        if method_name in ['post', 'put', 'delete']:
            method_kwargs['data'] = json.dumps(query)

        # call corresponding requests library method
        method = getattr(requests, method_name)
        response = method(uri, **method_kwargs)

        # Legitimate max 404 NotFound responses get a None in response
        # 404 responses caused by unimplemented methods, raise an exception
        if response.status_code in [404]:
            try:
                response.json()
                return None
            except ValueError:
                raise RequestError("Not Implemented: {} doesn't accept method {}".format(resource.uri, method_name))

        # Some proxy lives between max and the client, and something went wrong
        # on the backend site, probably max is stopped
        elif response.status_code in [502]:
            raise RequestError("Server {} responded with 502. Is max running?".format(self.url))

        # Successfull requests gets the json response in return
        # except HEAD ones, that gets the count
        elif response.status_code in [200, 201, 204]:
            if method_name == 'head':
                return int(response.headers.get('X-totalItems', 0))
            else:
                return response.json()

        # Everything else is treated as a max error response,
        # and so we expect to contain json, otherwise is an unknown error
        else:
            try:
                json_error = response.json()
                raise RequestError("{error}: {error_description}".format(**json_error))
            except:
                raise RequestError("Server responded with error {}".format(response.status_code))

    @property
    def client(self):
        return self

    @property
    def routes(self):
        """
            Parses the endpoint list on ROUTES, and transforms it to be accessed dict-like
            level by level.
        """
        routes = {}
        for route_name, route in ROUTES.items():
            parts = route['route'].split('/')[1:]
            last_path = routes
            for part in parts:
                last_path = last_path.setdefault(part, {})

        return routes

    def __getattr__(self, attr):
        """
            Returns a ResourceCollection  if the accessed attribute mathes
            a valid point in the current routes map
        """
        if attr in self.routes.keys():
            return ResourceCollection(self, attr)
        return AttributeError('Resource not found "{}"'.format(attr))
