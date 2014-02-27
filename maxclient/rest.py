from client import MaxClient as RPCMaxClient
from resources import RESOURCES as ROUTES
from functools import partial
import re
import json
import requests

DEFAULT_MAX_SERVER = 'http://localhost:8081'
DEFAULT_OAUTH_SERVER = 'https://oauth.upcnet.es'
DEFAULT_SCOPE = 'widgetcli'
DEFAULT_GRANT_TYPE = 'password'
DEFAULT_CLIENT_ID = 'MAX'


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
        return ResourceItem(self, key)


class ResourceItem(Resource):
    """
    """

    def __init__(self, parent, attr):
        self.parent = parent
        self.client = parent.client
        self._name = attr
        self.rest_param = self.get_rest_param()
        self.routes = parent.routes[self.rest_param]

    def get_rest_param(self):
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

        # Successfull requests gets the json response in return
        # except HEAD ones, that gets the count
        elif response.status_code in [200, 201, 204]:
            if method_name == 'head':
                return int(response.headers.get('X-totalItems', 0))
            else:
                return response.json()

        # Everything else is treated as a max error response,
        # and so we expect to contain json
        else:
            json_error = response.json()
            raise RequestError("{error}: {error_description}".format(**json_error))

    @property
    def client(self):
        return self

    @property
    def routes(self):
        routes = {}
        for route_name, route in ROUTES.items():
            parts = route['route'].split('/')[1:]
            last_path = routes
            for part in parts:
                last_path = last_path.setdefault(part, {})

        return routes

    def __getattr__(self, attr):
        if attr in self.routes.keys():
            return ResourceCollection(self, attr)
        return AttributeError('Resource not found "{}"'.format(attr))
