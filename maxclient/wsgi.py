from maxclient.rest import MaxClient as RestClient
from webtest import TestApp
from max import main


class MaxClient(RestClient):

    path = ''
    route = ''
    app = None

    def setToken(self, oauth2_token):
        super(MaxClient, self).setToken(oauth2_token)
        self.rest = RestClient(self.url, oauth_server=self.oauth_server)
        self.rest.actor = self.actor
        self.rest.token = self.token
        self.settings = self.rest.info.settings.get()
        self.url = ''

    @property
    def requester(self):
        import ipdb;ipdb.set_trace()
        if self.app is None:
            self.app = TestApp(main({}, **self.rest.info.settings()))
        return self.app

    def do_request(self, method_name, uri, params):
        method = getattr(self.requester, method_name)
        return method(uri, params.get('data', ''), params.get('headers', {}))

    def response_content(self, response):
        return response.text
