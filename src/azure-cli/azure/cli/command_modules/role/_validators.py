# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
from knack.util import CLIError
from ._client_factory import _graph_client_factory


VARIANT_GROUP_ID_ARGS = ['object_id', 'group_id', 'group_object_id']


def _get_group_count_and_id(namespace, group_filter):
    client = _graph_client_factory(namespace.cmd.cli_ctx)
    result = list(client.groups.list(filter=group_filter))
    return len(result), result[0].object_id if len(result) == 1 else None


def validate_group(namespace):
    # For AD auto-commands, here we resolve logic names to object ids needed by SDK methods
    attr, value = next(((x, getattr(namespace, x)) for x in VARIANT_GROUP_ID_ARGS
                        if hasattr(namespace, x)))
    try:
        uuid.UUID(value)
    except ValueError:
        exact_match_count, object_id = _get_group_count_and_id(namespace, "displayName eq '{}'".format(value))
        if exact_match_count == 1:
            setattr(namespace, attr, object_id)
        elif exact_match_count == 0:
            prefix_match_count, object_id = _get_group_count_and_id(
                namespace, "startswith(displayName,'{}')".format(value)
            )
            if prefix_match_count == 1:
                setattr(namespace, attr, object_id)
            elif prefix_match_count == 0:
                raise CLIError("No group matches the name of '{}'".format(value))
            else:
                raise CLIError("More than one group match the name of '{}'".format(value))
        else:
            raise CLIError("More than one group match the name of '{}'".format(value))


def validate_member_id(namespace):
    from azure.cli.core._profile import Profile
    cli_ctx = namespace.cmd.cli_ctx
    try:
        uuid.UUID(namespace.url)
        profile = Profile(cli_ctx=cli_ctx)
        _, _, tenant_id = profile.get_login_credentials()
        graph_url = cli_ctx.cloud.endpoints.active_directory_graph_resource_id
        namespace.url = '{}{}/directoryObjects/{}'.format(graph_url, tenant_id,
                                                          namespace.url)
    except ValueError:
        pass  # let it go, invalid values will be caught by server anyway


def validate_cert(namespace):
    cred_usage_error = CLIError('Usage error: --cert STRING | --create-cert [--keyvault VAULT --cert NAME] | '
                                '--password STRING | --keyvault VAULT --cert NAME')
    cert = namespace.cert
    create_cert = namespace.create_cert
    keyvault = namespace.keyvault

    # validate allowed parameter combinations
    if not any((cert, create_cert, keyvault)):
        # 1 - Simplest scenario. Use random password
        pass
    elif create_cert and not any((cert, keyvault)):
        # 3 - User-supplied public cert data
        pass
    elif cert and not any((create_cert, keyvault)):
        # 4 - Create local self-signed cert
        pass
    elif cert and keyvault:
        # 5 - Create self-signed cert in KeyVault
        # 6 - Use existing cert from KeyVault
        pass
    else:
        raise cred_usage_error

    # validate cert parameter
    if cert and not keyvault:
        from azure.cli.command_modules.role.custom import _try_x509_pem, _try_x509_der
        x509 = _try_x509_pem(cert) or _try_x509_der(cert)
        if not x509:
            raise CLIError('usage error: --cert STRING | --cert NAME --keyvault VAULT')
        namespace.cert = x509


def validate_change_password(namespace):
    if namespace.password is None and namespace.force_change_password_next_login is not None:
        raise CLIError("--force-change-password-next-login is only valid when --password is specified")


def process_assignment_namespace(cmd, namespace):  # pylint: disable=unused-argument
    # Make sure these arguments are non-empty strings.
    # When they are accidentally provided as an empty string "", they won't take effect when filtering the role
    # assignments, causing all matched role assignments to be listed/deleted. For example,
    #   az role assignment delete --assignee ""
    # removes all role assignments under the subscription.
    non_empty_args = ["assignee", "scope", "role", "resource_group_name"]
    non_empty_msg = "usage error: {} can't be an empty string. Either omit it or provide a non-empty string."

    for arg in non_empty_args:
        if getattr(namespace, arg) == "":
            # Get option name, like resource_group_name -> --resource-group
            option_name = cmd.arguments[arg].type.settings['options_list'][0]
            raise CLIError(non_empty_msg.format(option_name))

    resource_group = namespace.resource_group_name
    if namespace.scope and resource_group and getattr(resource_group, 'is_default', None):
        namespace.resource_group_name = None  # drop configured defaults
