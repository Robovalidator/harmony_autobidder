from builtins import object


class Validator(object):
    def __init__(self, address, name, bid, bls_keys, num_slots, uptime):
        self.address = address
        self.name = name
        self.bid = bid
        self.bls_keys = bls_keys
        self.num_slots = num_slots
        self.uptime = uptime

    def to_dict(self):
        return dict(
            address=self.address,
            name=self.name,
            bid=self.bid,
            bls_keys=self.bls_keys,
            num_slots=self.num_slots,
            uptime=self.uptime
        )

    @classmethod
    def from_dict(cls, data):
        return Validator(data["address"],
                         data["name"],
                         data["bid"],
                         data["bls_keys"],
                         data["num_slots"],
                         data["uptime"])

    def __str__(self):
        return u"Validator({})".format(self.to_dict())

    @property
    def uptime_as_pct(self):
        if self.uptime is None:
            return "unknown"
        return f"{round(self.uptime * 100.0, 5)}%"


class SlotRange(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @property
    def num_slots(self):
        return 1 + (self.end - self.start)

    def __str__(self):
        if self.num_slots == 1:
            return str(self.end)
        return u"{}-{}".format(self.start, self.end)

    def __repr__(self):
        return str(self)
