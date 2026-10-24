---
title: CMS Block UI Component
category: Magento 2 Extension
summary: >-
  A reusable UI component that renders a CMS block's content from a REST API,
  so you can drop CMS content into any layout — e.g. the checkout sidebar —
  without custom blocks.
github: https://github.com/trunglv/magento2_cms_ui_component
order: 6
---

### Overview

This module implements a UI component to render the content of a CMS block anywhere in a Knockout/UI Component layout. It fetches content from the REST API `/V1/cmsuicomponent/:blockId` and renders it, taking a `block_id` option — so it can be imported into any parent component or used standalone.

### Installation

Module path: `app/code/Betagento/CmsUiComponent`

```
bin/magento module:enable Betagento_CmsUiComponent
bin/magento setup:di:compile
bin/magento setup:static-content:deploy
```

### Example: add a CMS block to the checkout sidebar

Define a layout processor hook:

```xml
<type name="Magento\Checkout\Block\Onepage">
    <arguments>
        <argument name="layoutProcessors" xsi:type="array">
            <item name="cms_ui_component" xsi:type="object">Betagento\CmsUiComponent\Block\Checkout\LayoutProcessor\CmsUiComponentProcessor</item>
        </argument>
    </arguments>
</type>
```

```php
<?php

namespace Betagento\CmsUiComponent\Block\Checkout\LayoutProcessor;

use \Magento\Checkout\Block\Checkout\LayoutProcessorInterface;

class CmsUiComponentProcessor implements LayoutProcessorInterface
{
    public function process($jsLayout): array
    {
        $jsLayout['components']['checkout']['children']['sidebar']['children']['cms_static_block'] =
            [
                'component' => 'Betagento_CmsUiComponent/js/view/cms_block',
                'displayArea' => 'shipping-information',
                'config' => [
                    'block_id' => 'checkout_sidebar'
                ]
            ];

        return $jsLayout;
    }
}
```

### Support

Free and open-source. Issues and contributions welcome on the [GitHub repository](https://github.com/trunglv/magento2_cms_ui_component).
