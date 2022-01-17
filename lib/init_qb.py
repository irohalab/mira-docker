# noinspection PyPackageRequirements
from time import sleep

from colored import fg, attr
from qbittorrent import Client

MAX_RETRY_COUNT = 5


def update_qb(qb_username, qb_password):
    qb = Client('http://127.0.0.1:8091')
    api_version = None
    retry_count = 0
    while api_version is None and retry_count < MAX_RETRY_COUNT:
        try:
            api_version = qb.api_version()
        except:
            api_version = None
            retry_count = retry_count + 1
            sleep(5)
    qb.login('admin', 'adminadmin')
    qb.set_preferences(web_ui_username=qb_username, web_ui_password=qb_password)
    print(fg(119) + 'qBittorrent username and password updated successfully!' + attr('reset'))
