---
title: Concurrent/Multithreading Indexer
category: Magento 2 Performance
summary: >-
  Enables multithreaded reindexing for the Product Flat Indexer (not covered
  by Magento core) and swaps in spatie/fork as a faster, more modern
  multithreading backend.
github: https://github.com/trunglv/magento2_concurrent_indexer
order: 5
featured: true
---

### Overview

Magento 2 already supports multithreading for some indexers, but not all of them — notably, the Product Flat Indexer is left out. This module:

1. Enables the Product Flat Indexer to run concurrently.
2. Replaces Magento core's default multithreading with the [spatie/fork](https://github.com/spatie/fork) package, which is faster and more modern than the built-in implementation.

### Installation

```
composer require trunglv/magento2-concurrent_indexer
```

### Configuration

In `app/etc/env.php`, set the thread count (a Magento core setting) and enable the spatie/fork backend:

```php
'MAGE_INDEXER_THREADS_COUNT' => 3,
'BETA_CONCURRENT_INDEXER_THREADS_ENABLE' => 1
```

**Note:** `BETA_CONCURRENT_INDEXER_THREADS_ENABLE` must be set to use `spatie/fork`.

### How Magento core implements indexer multithreading

`\Magento\Catalog\Model\Indexer\Category\Product\Action::reindex()` builds a function per store and hands them to `\Magento\Indexer\Model\ProcessManager::execute()`:

```php
protected function reindex(): void
{
    $userFunctions = [];

    foreach ($this->storeManager->getStores() as $store) {
        if ($this->getPathFromCategoryId($store->getRootCategoryId())) {
            $userFunctions[$store->getId()] = function () use ($store) {
                $this->reindexStore($store);
            };
        }
    }

    $this->processManager->execute($userFunctions);
}
```

```php
public function execute($userFunctions)
{
    if ($this->threadsCount > 1 && $this->isCanBeParalleled() && !$this->isSetupMode() && PHP_SAPI == 'cli') {
        $this->multiThreadsExecute($userFunctions);
    } else {
        $this->simpleThreadExecute($userFunctions);
    }
}
```

### How this module implements it

`\Betagento\ConcurrentIndexer\Plugin\Indexer\AroundProcessManager` swaps in `spatie/fork` when enabled:

```php
if ($this->config->isEnabled() && $this->config->getThreadCount() > 1 && $this->config->isCanBeParalleled() && !$this->config->isSetupMode() && PHP_SAPI == 'cli') {

    \Spatie\Fork\Fork::new()->concurrent($this->config->getThreadCount())->run(...$userFunctions);
    return;
}
```

Passes `phpstan` level 9 clean (`vendor/bin/phpstan analyse app/code/Betagento/ConcurrentIndexer/ --level 9`).

### Support

Free and open-source. Issues and contributions welcome on the [GitHub repository](https://github.com/trunglv/magento2_concurrent_indexer).
