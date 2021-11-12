# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json

from azure.cli.core.util import send_raw_request
from azure.cli.core.auth.util import resource_to_scopes


class GraphClient:
    def __init__(self, cli_ctx):
        self.cli_ctx = cli_ctx
        self.scopes = resource_to_scopes(cli_ctx.cloud.endpoints.microsoft_graph_resource_id)

        # https://graph.microsoft.com/ (AzureCloud)
        self.resource = cli_ctx.cloud.endpoints.microsoft_graph_resource_id

        # https://graph.microsoft.com/v1.0
        self.base_url = cli_ctx.cloud.endpoints.microsoft_graph_resource_id + 'v1.0'

    def send(self, method, url, param=None, body=None):
        url = self.base_url + url

        if body:
            body = json.dumps(body)
        r = send_raw_request(self.cli_ctx, method, url, resource=self.resource, uri_parameters=param, body=body)
        if r.text:
            dic = r.json()
            if 'value' in dic:
                return dic['value']
            return r.json()
        else:
            return None

    # id is python built-in name: https://docs.python.org/3/library/functions.html#id
    # filter is python built-in name: https://docs.python.org/3/library/functions.html#filter

    def application_create(self, body):
        # https://docs.microsoft.com/en-us/graph/api/application-post-applications
        result = self.send("POST", "/applications", body=body)
        return result

    def application_show(self, id):
        # https://docs.microsoft.com/en-us/graph/api/application-get
        result = self.send("GET", "/applications/{id}".format(id=id))
        return result

    def application_list(self, filter=None):
        # https://docs.microsoft.com/en-us/graph/api/application-list
        result = self.send("GET", "/applications?$filter={}".format(filter))
        return result

    def application_delete(self, id):
        # https://docs.microsoft.com/en-us/graph/api/application-delete
        result = self.send("DELETE", "/applications/{id}".format(id=id))
        return result

    def application_owner_add(self, id, body):
        # https://docs.microsoft.com/en-us/graph/api/application-post-owners
        result = self.send("POST", "/applications/{id}/owners/$ref".format(id=id), body=body)
        return result

    def application_owner_list(self, id):
        # https://docs.microsoft.com/en-us/graph/api/application-list-owners
        result = self.send("GET", "/applications/{id}/owners".format(id=id))
        return result

    def application_owner_remove(self, id):
        # https://docs.microsoft.com/en-us/graph/api/application-delete-owners
        result = self.send("DELETE", "/applications/{id}/owners/{id}/$ref".format(id=id))
        return result

    def application_password_create(self, id):
        # https://docs.microsoft.com/en-us/graph/api/application-addpassword
        result = self.send("POST", "/applications/{id}/addPassword".format(id=id))
        return result

    def application_password_delete(self, id):
        # https://docs.microsoft.com/en-us/graph/api/application-addpassword
        result = self.send("POST", "/applications/{id}/removePassword".format(id=id))
        return result

    def service_principal_create(self, body):
        # https://docs.microsoft.com/en-us/graph/api/application-post-applications
        result = self.send("POST", "/servicePrincipals", body=body)
        return result

    def service_principal_show(self, id):
        # https://docs.microsoft.com/en-us/graph/api/application-get
        result = self.send("GET", "/servicePrincipals/{id}".format(id=id))
        return result

    def service_principal_list(self, filter=None):
        # https://docs.microsoft.com/en-us/graph/api/application-list
        result = self.send("GET", "/servicePrincipals?$filter={}".format(filter))
        return result

    def service_principal_delete(self, id):
        # https://docs.microsoft.com/en-us/graph/api/application-delete
        result = self.send("DELETE", "/servicePrincipals/{id}".format(id=id))
        return result

    def owned_objects_list(self):
        # https://docs.microsoft.com/en-us/graph/api/user-list-ownedobjects
        result = self.send("GET", "/me/ownedObjects")
        return result
