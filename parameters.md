# Mercari API Parameters Guide (Unofficial)

## API Request URL

https://api.mercari.jp/v2/entities:search

Request with POST.

Parameters below are set in dict `searchCondition` in the request payload.

## `attributes`

Type: list

## `brandId`

Type: list

## `categoryId`

Type: list of ints

## `colorId`

Type: list

<!-- ## `createdAfterDate`
## `createdBeforeDate` -->
## `excludeKeyword`

Type: string

## `hasCoupon`

Type: bool

## `itemConditionId`

Type: list of ints

- empty or \[1, 2, 3, 4, 5, 6\]: すべて
- 1: 新品、未使用
- 2: 未使用に近い
- 3: 目立った傷や汚れなし
- 4: やや傷や汚れあり
- 5: 傷や汚れあり
- 6: 全体的に状態が悪い

## `itemTypes`

Type: list

## `keyword`

Type: string

## `order`

Type: string

- "ORDER_DESC"
- "ORDER_ASC"

See class `MercariOrder` in [mercari.py](mercari/mercari.py).

## `priceMax`

Type: int

in range \[300, 9999999\]

## `priceMin`

Type: int

in range \[300, 9999999\]

<!-- ## `promotionValidAt` -->
## `sellerId`

Type: list

## `shippingFromArea`

Type: list

## `shippingMethod`

Type: list

## `shippingPayerId`

Type: list

## `shopIds`

Type: list

## `sizeId`

Type: list

## `skuIds`

Type: list

## `sort`

Type: string

- "SORT_DEFAULT"
- "SORT_CREATED_TIME"
- "SORT_NUM_LIKES"
- "SORT_SCORE"
- "SORT_PRICE"

See class `MercariSort` in [mercari.py](mercari/mercari.py).

## `status`

Type: list of strings

- "STATUS_DEFAULT" or \["STATUS_ON_SALE", "STATUS_SOLD_OUT", "STATUS_TRADING"\]: すべて
- "STATUS_ON_SALE": 販売中
- \["STATUS_SOLD_OUT", "STATUS_TRADING"\]: 売り切れ (in which STATUS_TRADING means the deal is ongoing, and STATUS_SOLD_OUT means the deal is complete)

See class `MercariSearchStatus` in [mercari.py](mercari/mercari.py).
