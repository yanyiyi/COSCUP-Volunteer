from requests import Session

import setting
from models.mattermostdb import MattermostUsersDB
from module.mattermost_link import MattermostLink
from models.oauth_db import OAuthDB


class MattermostBot(Session):
    def __init__(self, token, base_url):
        super(MattermostBot, self).__init__()
        self.token = token
        self.base_url = base_url

    def get(self, path, **kwargs):
        headers = {'Authorization': 'Bearer %s' % self.token}
        return super(MattermostBot, self).get('%s%s' % (self.base_url, path), headers=headers, **kwargs)

    def post(self, path, **kwargs):
        headers = {'Authorization': 'Bearer %s' % self.token}
        return super(MattermostBot, self).post('%s%s' % (self.base_url, path), headers=headers, **kwargs)

    def get_users(self, page, per_page=200):
        return self.get('/users', params={'page': page, 'per_page': per_page})

    def get_users_loop(self, per_page=200):
        page = 0
        n = 0
        for u in self.get_users(page=page, per_page=per_page).json():
            yield u
            n += 1

        while(n == per_page):
            page += 1
            n = 0
            for u in self.get_users(page=page, per_page=per_page).json():
                yield u
                n += 1

    def get_users_stats(self):
        return self.get('/users/stats')

    def get_user_by_username(self, username):
        return self.get('/users/username/%s' % username)

    def create_a_direct_message(self, users):
        return self.post('/channels/direct', json=users)

    def posts(self, channel_id, message):
        return self.post('/posts', json={'channel_id': channel_id, 'message': message})

    def get_posts_from_channel(self, channel_id):
        return self.get('/channels/%s/posts' % channel_id)


class MattermostTools(MattermostBot):
    ''' MattermostTools for more implement in operation '''
    def __init__(self, token, base_url):
        super(MattermostTools, self).__init__(token=token, base_url=base_url)

    def find_possible_mid(self, uid, mail=None):
        ''' Find any possible mattermost user id

        :param str uid: uid
        :param str mail: user mail

        '''
        mml = MattermostLink(uid)
        if 'data' in mml.raw and 'user_id' in mml.raw['data']:
            return mml.raw['data']['user_id']

        if mail is None:
            oauth = OAuthDB().find_one({'owner': uid}, {'_id': 1})
            if oauth:
                mail = oauth['_id']

        if mail:
            mm_user = MattermostUsersDB().find_one({'email': mail.strip()}, {'_id': 1})
            if mm_user:
                return mm_user['_id']

        return u''
