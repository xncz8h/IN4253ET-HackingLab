from dataclasses import dataclass


@dataclass
class DataCookie:
    name: str
    src_domain: str
    domain: str
    ttl: float
    trackers: []
    is_third_party: bool = True


class Cookie(object):
    def __init__(self, name, src_domain, domain, ttl, isThirdParty=False):
        self.name = name
        self.src_domain = src_domain
        self.domain = domain
        self.ttl = ttl
        self.isThirdParty = isThirdParty
        self.trackers = []
