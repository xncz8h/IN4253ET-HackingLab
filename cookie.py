

class Cookie:
    def __init__(self, name, src_domain, domain, ttl, isThirdParty):
        self.name = name
        self.src_domain = src_domain
        self.domain = domain
        self.ttl = ttl
        self.isThirdParty = isThirdParty
        self.trackers = []

    def __repr__(self):
        return f'Cookie(name={self.name}, src_domain={self.src_domain}, domain={self.domain}, ttl={self.ttl}, ' \
               f'isThirdParty={self.isThirdParty}, tracker={self.trackers})\n'


