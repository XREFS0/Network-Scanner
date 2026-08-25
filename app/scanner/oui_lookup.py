"""IEEE OUI (Organizationally Unique Identifier) vendor resolution database and lookup."""
import re
from typing import Dict

# Curated high-density hardware manufacturer database
OUI_DATABASE: Dict[str, str] = {
    # Apple
    "000393": "Apple", "000502": "Apple", "000A27": "Apple", "000A95": "Apple",
    "000D93": "Apple", "0010FA": "Apple", "001124": "Apple", "001451": "Apple",
    "0016CB": "Apple", "0017F2": "Apple", "0019E3": "Apple", "001B63": "Apple",
    "001C42": "Apple", "001D4F": "Apple", "001E52": "Apple", "001F5B": "Apple",
    "0021E9": "Apple", "002241": "Apple", "002312": "Apple", "002332": "Apple",
    "00236C": "Apple", "002436": "Apple", "002500": "Apple", "00254B": "Apple",
    "002608": "Apple", "00264A": "Apple", "0026B0": "Apple", "040CCE": "Apple",
    "041552": "Apple", "042665": "Apple", "045453": "Apple", "04DB56": "Apple",
    "080007": "Apple", "086698": "Apple", "087045": "Apple", "087402": "Apple",
    "0C74C2": "Apple", "1040F3": "Apple", "14109F": "Apple", "14205E": "Apple",
    "18AF61": "Apple", "207D74": "Apple", "28CFE9": "Apple", "34363B": "Apple",
    "3C0754": "Apple", "406C8F": "Apple", "484BFA": "Apple", "50BC96": "Apple",
    "5855CA": "Apple", "600308": "Apple", "68DBCA": "Apple", "705681": "Apple",
    "784F43": "Apple", "80E650": "Apple", "88665A": "Apple", "90B931": "Apple",
    "9801A7": "Apple", "A483E7": "Apple", "ACBC32": "Apple", "B8E856": "Apple",
    "C869CD": "Apple", "D4909C": "Apple", "DC2B2A": "Apple", "E0B9BA": "Apple",
    "F01898": "Apple", "F40F24": "Apple", "F4F15A": "Apple",

    # Intel
    "0002B3": "Intel", "000347": "Intel", "000423": "Intel", "0007E9": "Intel",
    "000E0C": "Intel", "001111": "Intel", "0012F0": "Intel", "001302": "Intel",
    "001320": "Intel", "0013CE": "Intel", "0013E8": "Intel", "001500": "Intel",
    "00166F": "Intel", "001676": "Intel", "0016EA": "Intel", "0018DE": "Intel",
    "0019D1": "Intel", "001A80": "Intel", "001B21": "Intel", "001C23": "Intel",
    "001D09": "Intel", "001D6B": "Intel", "001D72": "Intel", "001E64": "Intel",
    "001E65": "Intel", "001E67": "Intel", "00215C": "Intel", "00216A": "Intel",
    "0022FB": "Intel", "002315": "Intel", "0024D7": "Intel", "00270E": "Intel",
    "002710": "Intel", "081196": "Intel", "0C8BFD": "Intel", "1002B5": "Intel",
    "3413E8": "Intel", "484520": "Intel", "4851B7": "Intel", "4C79BA": "Intel",
    "5891CF": "Intel", "6805CA": "Intel", "7C5079": "Intel", "8086F2": "Intel",
    "8C8590": "Intel", "A036BC": "Intel", "A44CC8": "Intel", "C85B76": "Intel",
    "DC5360": "Intel", "E4A7C5": "Intel", "ECF451": "Intel", "F8633F": "Intel",

    # Cisco / Linksys
    "00000C": "Cisco", "000142": "Cisco", "000143": "Cisco", "000163": "Cisco",
    "000164": "Cisco", "000196": "Cisco", "000197": "Cisco", "0001C7": "Cisco",
    "0001C9": "Cisco", "000216": "Cisco", "000217": "Cisco", "00024A": "Cisco",
    "00024B": "Cisco", "00027D": "Cisco", "00027E": "Cisco", "0002B9": "Cisco",
    "0002BA": "Cisco", "0002FC": "Cisco", "0002FD": "Cisco", "000331": "Cisco",
    "000332": "Cisco", "00036B": "Cisco", "00036C": "Cisco", "00044D": "Cisco",
    "00044E": "Cisco", "00049F": "Cisco", "0004C0": "Cisco", "0004C1": "Cisco",
    "000531": "Cisco", "000532": "Cisco", "00055E": "Cisco", "000573": "Cisco",
    "00059A": "Cisco", "000628": "Cisco", "000652": "Cisco", "000653": "Cisco",
    "00070D": "Cisco", "00070E": "Cisco", "00074F": "Cisco", "000750": "Cisco",
    "000784": "Cisco", "000785": "Cisco", "0007B3": "Cisco", "0007B4": "Cisco",
    "0007EB": "Cisco", "0007EC": "Cisco", "000820": "Cisco", "000821": "Cisco",
    "00087C": "Cisco", "0008A3": "Cisco", "0008A4": "Cisco", "0008E2": "Cisco",
    "0008E3": "Cisco", "000943": "Cisco", "000944": "Cisco", "00097B": "Cisco",
    "00097C": "Cisco", "0009B7": "Cisco", "0009B8": "Cisco", "0009E8": "Cisco",
    "0009E9": "Cisco", "000A41": "Cisco", "000A42": "Cisco", "000A8A": "Cisco",
    "000A8B": "Cisco", "000AB7": "Cisco", "000AB8": "Cisco", "000AEB": "Cisco",
    "000AEC": "Cisco", "000B45": "Cisco", "000B46": "Cisco", "000B5F": "Cisco",
    "000BBE": "Cisco", "000BBF": "Cisco", "000BC7": "Cisco", "000BC8": "Cisco",
    "000C30": "Cisco", "000C31": "Cisco", "000C85": "Cisco", "000C86": "Cisco",
    "000CEB": "Cisco", "000CEC": "Cisco", "000D28": "Cisco", "000D29": "Cisco",
    "000D65": "Cisco", "000D66": "Cisco", "000DBC": "Cisco", "000DBD": "Cisco",
    "000E08": "Cisco", "000E09": "Cisco", "000E38": "Cisco", "000E39": "Cisco",
    "000E83": "Cisco", "000E84": "Cisco", "000ED7": "Cisco", "000ED8": "Cisco",
    "001120": "Cisco-Linksys", "001217": "Cisco-Linksys", "001310": "Cisco-Linksys",
    "0014BF": "Cisco-Linksys", "0016B6": "Cisco-Linksys", "001839": "Cisco-Linksys",

    # Samsung
    "0000F0": "Samsung", "000278": "Samsung", "0007AB": "Samsung", "000918": "Samsung",
    "000D44": "Samsung", "000DE0": "Samsung", "001247": "Samsung", "001377": "Samsung",
    "001599": "Samsung", "0015B9": "Samsung", "00166B": "Samsung", "00166C": "Samsung",
    "0017D5": "Samsung", "0018AF": "Samsung", "001A8A": "Samsung", "001BD7": "Samsung",
    "001D25": "Samsung", "001E7D": "Samsung", "001FAC": "Samsung", "002119": "Samsung",
    "002339": "Samsung", "0023C3": "Samsung", "002454": "Samsung", "002491": "Samsung",
    "0024E9": "Samsung", "002637": "Samsung", "00265D": "Samsung", "04180F": "Samsung",
    "0808C2": "Samsung", "14F42A": "Samsung", "2C598A": "Samsung", "4480EB": "Samsung",
    "508569": "Samsung", "5C0A5B": "Samsung", "78471D": "Samsung", "90187C": "Samsung",
    "B407F9": "Samsung", "C4731E": "Samsung", "CC07AB": "Samsung", "E47CF9": "Samsung",

    # TP-Link
    "0019E0": "TP-Link", "002127": "TP-Link", "0023CD": "TP-Link", "002586": "TP-Link",
    "04A151": "TP-Link", "14CC20": "TP-Link", "14EB5E": "TP-Link", "18A6F7": "TP-Link",
    "1C61B4": "TP-Link", "28EE52": "TP-Link", "30B5C2": "TP-Link", "50C7BF": "TP-Link",
    "54AF97": "TP-Link", "60E327": "TP-Link", "704F57": "TP-Link", "7405A5": "TP-Link",
    "788A20": "TP-Link", "8C210A": "TP-Link", "90F652": "TP-Link", "984827": "TP-Link",
    "A0F3C1": "TP-Link", "AC84C6": "TP-Link", "B04E26": "TP-Link", "B09575": "TP-Link",
    "C006C3": "TP-Link", "C025E9": "TP-Link", "C04A00": "TP-Link", "C46E1F": "TP-Link",
    "D807B6": "TP-Link", "E848B8": "TP-Link", "EC086B": "TP-Link", "F4EC38": "TP-Link",

    # Netgear
    "00095B": "Netgear", "000FB5": "Netgear", "00146C": "Netgear", "00184D": "Netgear",
    "001B2F": "Netgear", "001E2A": "Netgear", "001F33": "Netgear", "00223F": "Netgear",
    "0024B2": "Netgear", "0026F2": "Netgear", "04A151": "Netgear", "204E7F": "Netgear",
    "28C68E": "Netgear", "30469A": "Netgear", "4494FC": "Netgear", "841B5E": "Netgear",
    "9C3DCF": "Netgear", "A00460": "Netgear", "B07FB9": "Netgear", "C0FFD4": "Netgear",

    # Dell
    "00065B": "Dell", "000874": "Dell", "000BDB": "Dell", "000D56": "Dell",
    "000F1F": "Dell", "001143": "Dell", "00123F": "Dell", "001372": "Dell",
    "001422": "Dell", "0015C5": "Dell", "0016F0": "Dell", "00188B": "Dell",
    "0019B9": "Dell", "001A6B": "Dell", "001C23": "Dell", "001D09": "Dell",
    "001E4F": "Dell", "002170": "Dell", "002219": "Dell", "0023AE": "Dell",
    "0024E8": "Dell", "002564": "Dell", "0026B9": "Dell", "180373": "Dell",
    "24B6FD": "Dell", "3417EB": "Dell", "4C7625": "Dell", "74867A": "Dell",
    "842B2B": "Dell", "90B11C": "Dell", "B82A72": "Dell", "D4BE50": "Dell",

    # HP / Hewlett-Packard
    "0001E6": "Hewlett Packard", "0002A5": "Hewlett Packard", "000400": "Hewlett Packard",
    "000802": "Hewlett Packard", "000883": "Hewlett Packard", "000B86": "Hewlett Packard",
    "000E7F": "Hewlett Packard", "000F20": "Hewlett Packard", "001083": "Hewlett Packard",
    "00110A": "Hewlett Packard", "001279": "Hewlett Packard", "001321": "Hewlett Packard",
    "001438": "Hewlett Packard", "001560": "Hewlett Packard", "001635": "Hewlett Packard",
    "001708": "Hewlett Packard", "0018FE": "Hewlett Packard", "001A4B": "Hewlett Packard",
    "001B78": "Hewlett Packard", "001C25": "Hewlett Packard", "001CC4": "Hewlett Packard",
    "001E0B": "Hewlett Packard", "001F29": "Hewlett Packard", "00215A": "Hewlett Packard",
    "002264": "Hewlett Packard", "00237D": "Hewlett Packard", "002481": "Hewlett Packard",
    "0025B3": "Hewlett Packard", "002655": "Hewlett Packard", "10604B": "Hewlett Packard",
    "3C5282": "Hewlett Packard", "645106": "Hewlett Packard", "9457A5": "Hewlett Packard",

    # Raspberry Pi Foundation
    "B827EB": "Raspberry Pi", "DC2632": "Raspberry Pi", "E45F01": "Raspberry Pi",
    "28CDC1": "Raspberry Pi", "D83ADD": "Raspberry Pi",

    # Espressif (ESP8266/ESP32 IoT)
    "18FE34": "Espressif", "240AC4": "Espressif", "246F28": "Espressif",
    "24B2DE": "Espressif", "2C3AE8": "Espressif", "30AEA4": "Espressif",
    "3C71BF": "Espressif", "483FDA": "Espressif", "4C11AE": "Espressif",
    "5C0272": "Espressif", "68C63A": "Espressif", "84CCA8": "Espressif",
    "84F3EB": "Espressif", "8C4B14": "Espressif", "94B97E": "Espressif",
    "A020A6": "Espressif", "A4CF12": "Espressif", "AC67B2": "Espressif",
    "B4E62D": "Espressif", "BCFF4D": "Espressif", "C44F33": "Espressif",
    "CC50E3": "Espressif", "D8A01D": "Espressif", "DC4F22": "Espressif",

    # VMware / VirtualBox / Hyper-V / QEMU
    "000569": "VMware", "000C29": "VMware", "001C14": "VMware", "005056": "VMware",
    "080027": "Oracle VirtualBox",
    "00155D": "Microsoft Hyper-V",
    "525400": "QEMU / KVM",

    # Xiaomi / Huawei
    "001E10": "Huawei", "00259E": "Huawei", "00464B": "Huawei", "04F938": "Huawei",
    "0876FF": "Huawei", "0C37DC": "Huawei", "101B54": "Huawei", "18DE36": "Huawei",
    "009E48": "Xiaomi", "04CF4B": "Xiaomi", "0C1DAE": "Xiaomi", "14ABB5": "Xiaomi",
    "185936": "Xiaomi", "286C07": "Xiaomi", "3480B3": "Xiaomi", "584498": "Xiaomi",

    # Realtek / Broadcom
    "0000E8": "Accton / Realtek", "000272": "Realtek", "000732": "Realtek",
    "0010A7": "Realtek", "00E04C": "Realtek", "52544C": "Realtek",
    "000AF7": "Broadcom", "001018": "Broadcom", "001BE9": "Broadcom",
}


def lookup_vendor(mac_address: str) -> str:
    """Resolves MAC address prefix to hardware manufacturer."""
    if not mac_address or mac_address.lower() in ("unknown", "n/a", ""):
        return "Unknown"

    clean_mac = re.sub(r"[^0-9A-Fa-f]", "", mac_address).upper()
    if len(clean_mac) >= 6:
        prefix = clean_mac[:6]
        return OUI_DATABASE.get(prefix, "Generic / Unknown")
    return "Unknown"
