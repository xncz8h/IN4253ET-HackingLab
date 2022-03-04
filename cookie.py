class Cookie(object):
    def __init__(self, name, src_domain, domain, ttl, isThirdParty=False):
        self.name = name
        self.src_domain = src_domain
        self.domain = domain
        self.ttl = ttl
        self.isThirdParty = isThirdParty
        self.trackers = []
    