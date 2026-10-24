---
title: "Customer data can't be found in Local Storage of a browser"
date: 2020-05-08 14:09:12 +0700
categories: [magento2]
---

[Link an issue: magento/magento2#14912](https://github.com/magento/magento2/issues/14912)

I came across this issue on my customer website. I added a downloadable product (which needs login to checkout), then I logged in, but when I clicked on the checkout button in the cart sidebar, it gave me an authentication popup.

Due to customer data on Local Storage not being loaded/initiated, my solution is to check whether customer data exists on Local Storage or not. Then if it doesn't, we make it expired, so it gets loaded again from the server.

Here's a quick fix for this issue below. But I think the Magento team should check and fix this issue properly.

Create a mixin:

```js
var config = {
 config: {
     mixins: {
         'Magento_Customer/js/customer-data': {

             'FixBugs_CustomerLocalStorageIssue/js/customer-data-mixin': true

         }
     }
 }
};

/**
 * trunglv - Fixing bugs
 *
 */
define([
    'jquery',
    'mage/utils/wrapper'
], function ($, wrapper) {
    'use strict';

    var mixin = {
        /**
         * @param {Function} originFn - Original method.
         * @return {Array}
         */
        getExpiredSectionNames: function (originFn) {
            var expiredSectionNames = originFn(),
                storage = $.initNamespaceStorage('mage-cache-storage').localStorage,
                sectionData;

            /* to add more if you want. It's a temporary fix for customer data on local storage */
            var sectionNames = ['customer'];

            _.each(sectionNames, function (sectionName) {

                sectionData = storage.get(sectionName);

                if (typeof sectionData === 'undefined') {
                        expiredSectionNames.push(sectionName);
                }

            });
            return expiredSectionNames;
        }
    };

    /**
     * Override default customer-data.getExpiredSectionNames().
     */
    return function (target) {
        return wrapper.extend(target, mixin);
    };
});
```

— Another solution, but needs a core fix —

Add section "customer" into `expiredSectionNames`:

```xml
<type name="Magento\Customer\Block\CustomerData">
    <arguments>
        <argument name="expirableSectionNames" xsi:type="array">
            <item name="customer" xsi:type="string">customer</item>
        </argument>
    </arguments>
</type>
```

In JS file: `Magento_Customer/js/customer-data`

```js
getExpiredSectionNames: function () {
            var expiredSectionNames = [],
                cookieSectionTimestamps = $.cookieStorage.get('section_data_ids') || {},
                sectionLifetime = options.expirableSectionLifetime * 60,
                currentTimestamp = Math.floor(Date.now() / 1000),
                sectionData;

            // process sections that can expire due to lifetime constraints
            _.each(options.expirableSectionNames, function (sectionName) {
                sectionData = storage.get(sectionName);

                if (typeof sectionData === 'object' && sectionData['data_id'] + sectionLifetime <= currentTimestamp) {
                    expiredSectionNames.push(sectionName);
                }else{
                    /* Here is my fixing*/
                    if(typeof sectionData == 'undefined'){
                        expiredSectionNames.push(sectionName);
                    }
                }
            });

            // process sections that can expire due to storage information inconsistency
            _.each(cookieSectionTimestamps, function (cookieSectionTimestamp, sectionName) {
                sectionData = storage.get(sectionName);

                if (typeof sectionData === 'undefined' ||
                    typeof sectionData === 'object' &&
                    cookieSectionTimestamp != sectionData['data_id'] //eslint-disable-line
                ) {
                    expiredSectionNames.push(sectionName);
                }
            });

            return _.uniq(expiredSectionNames);
        },
```

If you run into this issue, feel free to reach out — happy to compare notes.
