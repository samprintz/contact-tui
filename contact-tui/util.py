import configparser


def load_config(path):
    cfg = configparser.ConfigParser()
    cfg.read(path)
    config = {
            'path': {
                'rdf_file': cfg.get('paths', 'rdf_file'),
                'notes_dir': cfg.get('paths', 'notes_dir')
                },
            'rdf': {
                'namespace': cfg.get('rdf', 'namespace')
                },
            'encryption': {
                'keyid': cfg.get('encryption', 'keyid')
                },
            'google': {
                'credentials_file': cfg.get('google', 'credentials_file'),
                'token_file': cfg.get('google', 'token_file')
                },
            'editor': 'vim',
            'display': {
                'nav_width': cfg.getint('display', 'nav_width'),
                'palette': [
                    ('selected', '', 'light gray'),
                    ],
                'focus_map': {
                    'options': 'focus options'}
                }
            }
    return config