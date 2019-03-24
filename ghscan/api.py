from ghscan.exceptions.base import WhereError
from ghscan.constants import ALLOWED_SEARCH
from ghscan.utils import get_or_create_node
from http.cookiejar import MozillaCookieJar
from ghscan.abstractions import github
from http.cookiejar import LoadError
from urllib import request, error
from urllib import parse
import logging


class GitHubApi(github.GitHub):
    base_url = 'https://api.github.com/search'

    def __init__(self):

        self.logger = logging.getLogger('ghscan')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(get_or_create_node('ghscan.log'))
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.debug('Creating an instance of GitGubApi class')

        self.cj = MozillaCookieJar()
        self.cookie_file_name = get_or_create_node()
        self.need_auth = 1
        try:
            self.cj.load(self.cookie_file_name)
            self.need_auth = 0
            self.logger.debug('Auth: no auth needed')
        except LoadError as e:
            pass
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                          '(KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',

        }

    @classmethod
    def construct_url(cls, query, where, *args, **kwargs):
        if where not in ALLOWED_SEARCH:
            raise WhereError

        constructed = cls.base_url + '/' + where + '?q=' + query
        in_ = kwargs.get('in_', None)
        language = kwargs.get('language', None)
        repo = kwargs.get('repo', None)

        if in_:
            constructed = constructed + '+in:{in_}'.format(in_=in_)
        if language:
            constructed = constructed + '+language:{language}'.format(language=language)
        if repo:
            constructed = constructed + '+repo:{repo}'.format(repo=repo)
        return constructed

    def auth(self):
        pass

    def search(self, query, *args, **kwargs):
        where = kwargs.get('where', 'code')
        process_url = GitHubApi.construct_url(query, *args, **kwargs)
        self.logger.debug('search: {0}'.format(query))
        if where == 'topics':
            self.headers.update({'Accept': 'application/vnd.github.mercy-preview+json'})
        return self.get_data(process_url)

    def get_data(self, url, values=None, proxy=None):
        if url is None:
            return None
        if values:
            data = parse.urlencode(values).encode("utf-8")
        else:
            data = None

        try:
            self.logger.debug('Request URL: {0}'.format(url))
            req = request.Request(url, headers=self.headers, data=data)

            cookie = self.cj
            cookie_process = request.HTTPCookieProcessor(cookie)
            opener = request.build_opener(cookie_process)
            if proxy:
                proxies = {parse.urlparse(url).scheme: proxy}
                opener.add_handler(request.ProxyHandler(proxies))
            content = opener.open(req).read()
            self.cj.save(self.cookie_file_name, ignore_discard=True, ignore_expires=True)
        except error.URLError as e:
            self.logger.debug('Error: {0}'.format(e))
            print('error', e)
            content = None

        self.logger.debug('Request URL success: {0}'.format(url))
        return content
