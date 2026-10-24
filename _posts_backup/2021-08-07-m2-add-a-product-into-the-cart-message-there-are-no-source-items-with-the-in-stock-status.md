---
title: 'Add a product into the cart – message "There are no source items with the in-stock status"'
date: 2021-08-07 14:09:12 +0700
categories: [magento2]
---

A bug story: I faced an issue on my customer website where a few products couldn't be added to the cart. The error message was "There are no source items with the in-stock status". After deeply debugging (see the steps below), I realized this SQL returns an empty result:

```sql
SELECT `main_table`.* FROM `inventory_source_item` AS `main_table`
WHERE ((`sku` = 'XXX-YYY')) AND ((`source_code` IN('default')))
AND ((`status` = 1))
```

Strangely, everything in the backend showed that the product had a qty of 2 and in-stock status. Then I went to MySQLAdmin to find the record related to the product SKU in the `inventory_source_item` table. It showed a record with `qty = 0` and `status = 0`.

I was sure we had reindexed a thousand times. I tried to save the product again from the backend, and — amazingly — it worked, and the qty/stock status were updated correctly in `inventory_source_item` for that product.

I think the problem happened because we migrated data from Magento 1 to Magento 2.

Here's a quick fix for this issue, for every product, without saving each one individually from the backend.

**NOTE!** In case you only have one stock source: "default".

- Backup table `inventory_source_item`
- Truncate table `inventory_source_item`

```sql
INSERT INTO inventory_source_item (`source_code`,`sku`, `quantity`, `status`)
(
 SELECT 'default', t_p.`sku`, t_status.`qty`, t_status.`stock_status`
 FROM cataloginventory_stock_status t_status
 INNER JOIN catalog_product_entity t_p ON t_p.entity_id = t_status.product_id
)
ON DUPLICATE KEY UPDATE status = status , quantity = quantity;
```

## Debug

**`Magento\InventorySales\Model\IsProductSalableForRequestedQtyCondition\IsAnySourceItemInStockCondition`**

```php
public function execute(string $sku, int $stockId, float $requestedQty): ProductSalableResultInterface
{
        $errors = [];

        if (!$this->isAnySourceInStockCondition->execute($sku, $stockId)) {
            $data = [
                'code' => 'is_any_source_item_in_stock-no_source_items_in_stock',
                'message' => __('There are no source items with the in stock status')
            ];
            $errors[] = $this->productSalabilityErrorFactory->create($data);
        }

        return $this->productSalableResultFactory->create(['errors' => $errors]);
}
```
