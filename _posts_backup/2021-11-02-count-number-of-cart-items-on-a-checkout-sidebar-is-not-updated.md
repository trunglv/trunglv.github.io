---
title: A count number of cart items on a checkout sidebar is not updated
date: 2021-11-02 14:09:12 +0700
categories: [magento2]
---

Today, 21 Nov 2021. Magento 2.4.3

The issue: when a customer applies a coupon code to add a new item on the checkout page, everything works perfectly, except the count number of cart items on the checkout sidebar is not updated.

![My helpful screenshot]({{ "/assets/posts/nov/cart_number_items.jpg" | relative_url }})

## Problem-solving

The problem is the count value is not calculated on an Observable Object (a KnockoutJS object).

Check files:

- JS component: `vendor/magento/module-checkout/view/frontend/web/js/view/summary/cart-items.js`
- Template: `vendor/magento/module-checkout/view/frontend/web/template/summary/cart-items.html`

The count number comes from a function `getCartSummaryItemsCount` of the view component `Magento_Checkout/view/summary/cart-items`:

```js
/**
 * Returns cart items qty
 *
 * @returns {Number}
 */
getItemsQty: function () {
    return parseFloat(this.totals['items_qty']);
},

/**
 * Returns count of cart line items
 *
 * @returns {Number}
 */
getCartLineItemsCount: function () {
    return parseInt(totals.getItems()().length, 10);
},
```

But you can see a property `totals` is not an observable object:

```js
return Component.extend({
    defaults: {
        template: 'Magento_Checkout/summary/cart-items'
    },
    totals: totals.totals(),
    // ...
```

A solution is: find the text `/*FIXED HERE*/` below to see what I changed.

```js
/**
 * Copyright © Magento, Inc. All rights reserved.
 * See COPYING.txt for license details.
 */

define([
    'ko',
    'Magento_Checkout/js/model/totals',
    'uiComponent',
    'Magento_Checkout/js/model/step-navigator',
    'Magento_Checkout/js/model/quote'
], function (ko, totals, Component, stepNavigator, quote) {
    'use strict';

    var useQty = window.checkoutConfig.useQty;

    return Component.extend({
        defaults: {
            template: 'Magento_Checkout/summary/cart-items'
        },
        /*-------- FIXED HERE ---------- */
        /* previous: totals: totals.totals() => remove "()" to keep an observable object */
        totals: totals.totals,
        /*---------END- FIXED HERE -------*/
        items: ko.observable([]),
        maxCartItemsToDisplay: window.checkoutConfig.maxCartItemsToDisplay,
        cartUrl: window.checkoutConfig.cartUrl,

        /**
         * @deprecated Please use observable property (this.items())
         */
        getItems: totals.getItems(),

        /**
         * Returns cart items qty
         *
         * @returns {Number}
         */
        getItemsQty: function () {
            /*------ FIXED HERE -------*/
            /* previous: return parseFloat(this.totals['items_qty']); */
            return parseFloat(this.totals()['items_qty']);
            /*------ END - FIXED HERE -------*/
        },

        /**
         * Returns count of cart line items
         *
         * @returns {Number}
         */
        getCartLineItemsCount: function () {
            return parseInt(totals.getItems()().length, 10);
        },

        /**
         * Returns shopping cart items summary (includes config settings)
         *
         * @returns {Number}
         */
        getCartSummaryItemsCount: function () {

            return useQty ? this.getItemsQty() : this.getCartLineItemsCount();
        },

        /**
         * @inheritdoc
         */
        initialize: function () {
            this._super();
            // Set initial items to observable field
            this.setItems(totals.getItems()());
            // Subscribe for items data changes and refresh items in view
            totals.getItems().subscribe(function (items) {
                this.setItems(items);
            }.bind(this));
        },

        /**
         * Set items to observable field
         *
         * @param {Object} items
         */
        setItems: function (items) {
            if (items && items.length > 0) {
                items = items.slice(parseInt(-this.maxCartItemsToDisplay, 10));
            }
            this.items(items);
        },

        /**
         * Returns bool value for items block state (expanded or not)
         *
         * @returns {*|Boolean}
         */
        isItemsBlockExpanded: function () {
            return quote.isVirtual() || stepNavigator.isProcessed('shipping');
        }
    });
});
```
