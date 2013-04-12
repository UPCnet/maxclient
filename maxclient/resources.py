# Newest definitions (29/01/2013)
OAUTH_RESOURCES = {
    'users': {'route': '/people'},  # documented
    'user': {'route': '/people/{username}'},  # documented
    'avatar': {'route': '/people/{username}/avatar'},  # documented
    'user_activities': {'route': '/people/{username}/activities'},  # documented
    'timeline': {'route': '/people/{username}/timeline'},  # documented
    'user_comments': {'route': '/people/{username}/comments'},  # not implemented
    'user_shares': {'route': '/people/{username}/shares'},  # not implemented
    'user_likes': {'route': '/people/{username}/likes'},  # not implemented
    'follows': {'route': '/people/{username}/follows'},  # not implemented
    'follow': {'route': '/people/{username}/follows/{followedDN}'},  # not implemented
    'subscriptions': {'route': '/people/{username}/subscriptions'},  # documented
    'subscription': {'route': '/people/{username}/subscriptions/{hash}'},  # not implemented
    'user_conversations': {'route': '/people/{username}/conversations'},  # not implemented

    'activities': {'route': '/activities'},  # documented
    'activity': {'route': '/activities/{activity}'},  # not public API
    'comments': {'route': '/activities/{activity}/comments'},  # documented
    'comment': {'route': '/activities/{activity}/comments/{commentId}'},  # not implemented
    'likes': {'route': '/activities/{activity}/likes'},  # not implemented
    'like': {'route': '/activities/{activity}/likes/{likeId}'},  # not implemented
    'shares': {'route': '/activities/{activity}/shares'},  # not implemented
    'share': {'route': '/activities/{activity}/shares/{shareId}'},  # not implemented

    'contexts': {'route': '/contexts'},  # documented
    'context': {'route': '/contexts/{hash}'},  # documented
    'context_avatar': {'route': '/contexts/{hash}/avatar'},  # documented
    'context_permissions': {'route': '/contexts/{hash}/permissions'},
    'context_user_permissions': {'route': '/contexts/{hash}/permissions/{username}'},
    'context_user_permission': {'route': '/contexts/{hash}/permissions/{username}/{permission}'},

    'conversations': {'route': '/conversations'},  # documented
    'conversation': {'route': '/conversations/{hash}'},  # documented
    'messages': {'route': '/conversations/{hash}/messages'}  # not documented

}

ADMIN_RESOURCES = {
    'admin_user_activities': {'route': '/people/{username}/activities'},
    'admin_context_activities': {'route': '/contexts/{hash}/activities'},
    'admin_users': {'route': '/people'},
    'admin_activities': {'route': '/activities'},
    'admin_contexts': {'route': '/contexts'},

    'admin_user': {'route': '/people/{id}'},
    'admin_activity': {'route': '/activities/{id}'},
    'admin_context': {'route': '/contexts/{id}'},

    'admin_security': {'route': '/admin/security'},
}

ROUTES = {}
ROUTES.update(OAUTH_RESOURCES)
ROUTES.update(ADMIN_RESOURCES)
