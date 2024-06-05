import uuid
import json
import requests
import time
import logging
import re
from typing import Tuple, List

from .DpopUtils import generate_DPOP

rootURL = "https://api.mercari.jp/"
mercariIdPattern = r"[a-z][0-9]{11}"
mercariRootProductURL = "https://jp.mercari.com/item/"
mercariShopsPattern = r"[a-zA-Z0-9]{22}"
mercariShopsRootProductURL = "https://jp.mercari.com/shops/product/"
searchURL = "{}v2/entities:search".format(rootURL)


class MercariSearchStatus:
    DEFAULT = "STATUS_DEFAULT"
    ON_SALE = "STATUS_ON_SALE"
    SOLD_OUT = "STATUS_SOLD_OUT"
    TRADING = "STATUS_TRADING"


class MercariSort:
    SORT_DEFAULT = 'SORT_DEFAULT'
    SORT_CREATED_TIME = 'SORT_CREATED_TIME'
    SORT_NUM_LIKES = 'SORT_NUM_LIKES'
    SORT_SCORE = 'SORT_SCORE'
    SORT_PRICE = 'SORT_PRICE'

class MercariOrder:
    ORDER_DESC = 'ORDER_DESC'
    ORDER_ASC = 'ORDER_ASC'

class MercariItemStatus:
    ITEM_STATUS_UNSPECIFIED = 'ITEM_STATUS_UNSPECIFIED'
    ITEM_STATUS_ON_SALE = 'ITEM_STATUS_ON_SALE'
    ITEM_STATUS_TRADING = 'ITEM_STATUS_TRADING'
    ITEM_STATUS_SOLD_OUT = 'ITEM_STATUS_SOLD_OUT'
    ITEM_STATUS_STOP = 'ITEM_STATUS_STOP'
    ITEM_STATUS_CANCEL = 'ITEM_STATUS_CANCEL'
    ITEM_STATUS_ADMIN_CANCEL = 'ITEM_STATUS_ADMIN_CANCEL'

class Item:
    def __init__(self, *args, **kwargs):
        self.id = kwargs['productID']
        if re.fullmatch(mercariIdPattern, kwargs['productID']):
            self.productURL = "{}{}".format(mercariRootProductURL, kwargs['productID'])
        else:
            self.productURL = "{}{}".format(mercariShopsRootProductURL, kwargs['productID'])
        self.imageURL = kwargs['imageURL']
        self.productName = kwargs['name']
        self.price = kwargs['price']
        self.status = kwargs['status']
        self.soldOut = kwargs['status'] != MercariItemStatus.ITEM_STATUS_SOLD_OUT

    @staticmethod
    def fromApiResp(apiResp):
        return Item(
            productID=apiResp['id'],
            name=apiResp["name"],
            price=apiResp["price"],
            status=apiResp['status'],
            imageURL=apiResp['thumbnails'][0],
        )


# returns [] if resp has no items on it
# returns [Item's] otherwise
def parse(resp):
    if(len(resp["items"]) == 0):
        return [], False, None

    respItems = resp["items"]
    nextPageToken = resp["meta"]["nextPageToken"]
    return [Item.fromApiResp(item) for item in respItems], bool(nextPageToken), nextPageToken


def fetch(url, data):
    DPOP = generate_DPOP(
        # let's see if this gets blacklisted, but it also lets them track
        uuid="Mercari Python Bot",
        method="POST",
        url=url,
    )

    headers = {
        'DPOP': DPOP,
        'X-Platform': 'web',  # mercari requires this header
        'Accept': '*/*',
        'Accept-Encoding': 'deflate, gzip',
        'Content-Type': 'application/json; charset=utf-8',
        # courtesy header since they're blocking python-requests (returns 0 results)
        'User-Agent': 'python-mercari',
    }
    
    serializedData = json.dumps(data, ensure_ascii=False).encode('utf-8')

    r = requests.post(url, headers=headers, data=serializedData)

    r.raise_for_status()

    return parse(r.json())

# not sure if the v1 prefix ever changes, but from quick testing, doesn't seem like it
def pageToPageToken(page):
    return "v1:{}".format(page)

# returns an generator for Item objects
# keeps searching until no results so may take a while to get results back

def search(keywords, exclude_keywords="", sort=MercariSort.SORT_CREATED_TIME, order=MercariOrder.ORDER_DESC, status=MercariSearchStatus.ON_SALE, category_id: List[int] = [], price_max: int = 0, price_min: int = 0, item_condition_id: List[int] = [], total_page_limit=20, request_interval=1) -> Tuple[bool, List[Item]]:

    # This is per page and not for the final result
    limit = 120

    data = {
        # this seems to be random, but we'll add a prefix for mercari to track if they wanted to
        "userId": "MERCARI_BOT_{}".format(uuid.uuid4()), 
        "pageSize": limit,
        "pageToken": pageToPageToken(0),
        # same thing as userId, courtesy of a prefix for mercari
        "searchSessionId": "MERCARI_BOT_{}".format(uuid.uuid4()),
        # this is hardcoded in their frontend currently, so leaving it
        "indexRouting": "INDEX_ROUTING_UNSPECIFIED",
        "searchCondition": {
            "keyword": keywords,
            "excludeKeyword": exclude_keywords,
            "sort": sort,
            "order": order,
            "status": [status],
            "categoryId": category_id, # strange: "category_id" would do too
            "priceMin": price_min,
            "priceMax": price_max,
            "itemConditionId": item_condition_id,
        },
        # I'm not certain what these are, but I believe it's what mercari queries against
        # this is the default in their site, so leaving it as these 2
        "defaultDatasets": [
            "DATASET_TYPE_MERCARI",
            "DATASET_TYPE_BEYOND"
        ]
    }

    has_next_page = True
    total_page = 0

    result = []
    initial_request_interval = request_interval

    while has_next_page:
        total_page += 1
        print(f"fetching {keywords}, page {total_page}")
        while True:
            try:
                items, has_next_page, next_page_token = fetch(searchURL, data)
                request_interval -= initial_request_interval
                if request_interval <= 0:
                    request_interval = initial_request_interval
                break
            except requests.exceptions.HTTPError as e:
                print(f"Fetch error, sleep for {request_interval}s:\n{e}")
                logging.error(f"Fetch error, sleep for {request_interval}s:\n{e}", exc_info=True)
                time.sleep(request_interval)
                request_interval *= 2
                if request_interval >= 600:
                    return False, []
        result += items
        data['pageToken'] = next_page_token
        if total_page > total_page_limit:
            break
        time.sleep(request_interval)
    return True, result
