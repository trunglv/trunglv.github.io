---
title: Custom Order Number
category: Magento 2 Extension
summary: >-
  Build flexible order numbers using an easy expression syntax, e.g.
  {website_code}-{customer.customer_group}-{month}-{SEQUENCE_NUMBER}. Works
  for orders, invoices, and shipments.
github: https://github.com/trunglv
order: 1
---

### Overview

I built this extension to help you manage order numbers more flexibly. The default order number functionality in Magento is simple — it just increments numbers by store scope. This extension lets you do a lot more.

For example, you might want an order number like `DE-B2B-04-00023`, where `DE` is the country code, `B2B` is the customer group, and `04` is the month the order was placed. Read on for how to set this up.

### Key features

- Easy-to-use expression syntax to define an order number, e.g. `{website_code}-{customer.customer_group}-{month}-{SEQUENCE_NUMBER}`
- Works for orders, invoices, and shipments

### How to use it

#### Configuration

Go to **Store » Configuration » Betagento » Custom Order Number**.

#### 1. Pattern/Expression — defines the format of an order number

Variables already supported:

```
{SEQUENCE_NUMBER} : Sequence Number (0000xxx)
{date} : Date number
{month} : Month number
{year} : Year number
{website_code} : Website code
{customer_group} : Customer Group
```

Billing address attributes:

```
billing_company : Company
billing_country_id : Country ID (DE,DK)
billing_postcode : Post code
```

Shipping address attributes:

```
{shipping_country_id} : Country
{shipping_postcode} : Post code
```

If you want more, please contact me (Trung) at [luuvantrung@gmail.com](mailto:luuvantrung@gmail.com).

#### 2. Zero padding

The counter is zero-padded; the default width is 9 digits.

#### 3. Use sequence per website scope

The sequence number is calculated by website scope, not store scope.

### Support

Want it adjusted, or need more features? Get in touch at [luuvantrung@gmail.com](mailto:luuvantrung@gmail.com).

This extension is free and open-source. Feel free to open an issue or a pull request on the repository.
