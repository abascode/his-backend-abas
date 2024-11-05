from xid import XID


def generate_xid() -> str:
    return XID().string().upper()
