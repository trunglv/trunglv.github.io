---
title: Mage2 Dev Tool
category: Magento 2 CLI Tooling
summary: >-
  A set of bin/magento CLI debug tools for Magento 2 — inspect DI,
  plugins, observers, controller actions, and API reflection, plus a
  built-in MCP server so AI agents can query your Magento install directly.
github: https://github.com/trunglv/mage2_dev
order: 4
featured: true
---

### Overview

`mage2_dev` is a collection of `bin/magento` CLI commands to help debug Magento 2's Dependency Injection, plugin, and event system without digging through generated code by hand. It also ships an MCP server so AI coding agents (Claude Code, Claude Desktop, Cursor, VS Code Copilot, Codex) can query the same information directly.

### Installation

Install via Composer (recommended):

```
composer require trunglv/mage2-dev:dev-main
```

Or clone the source into `app/code/Betagento`.

### Debug tools

#### Dependency Injection checking

Inspect preferences and interceptor/factory chains for a given class. Run `setup:di:compile` first so DI configs (preferences, interceptors, factories) are generated.

```
php bin/magento beta_dev:check_di -t "Magento\Quote\Model\QuoteManagement"
```

#### List all plugins by listener type

List every plugin registered for a scope, filtered by listener type (`before`, `around`, `after`).

```
bin/magento beta_dev:show_plugins_by_listener_type -t around
```

#### List all plugins for a class

```
bin/magento beta_dev:show_plugins -t "Magento\InventorySales\Model\AreProductsSalableForRequestedQty"
```

Shows plugins injected on the interface itself and on its preference concrete class, grouped by scope (global, frontend, adminhtml, webapi_rest, webapi_soap, graphql).

#### List all observers for an event

```
bin/magento beta_dev:show_observers -e catalog_product_get_final_price
```

```
Options:
  -e, --event=EVENT              Event code
  -s, --scope_code[=SCOPE_CODE]  Scope : global|frontend|adminhtml|crontab|webapi_rest|webapi_soap|graphql
```

#### Show all controller actions per scope

```
bin/magento beta_dev:show_controller_action -f checkout -a frontend
```

```
Options:
  -f, --frontname=FRONTNAME  Frontname, e.g. catalog
  -a, --area=AREA            Area Code: frontend|adminhtml
```

#### Reflection for API services

```
bin/magento beta_dev:api_reflection --api "/V1/carts/:cartId/shipping-information" -m POST
```

```
Options:
  -a, --api=API                    API ID
  -m, --http_method[=HTTP_METHOD]  HTTP Method
```

Shows general info, input data reflection, and output data reflection for a given REST API.

### MCP server (for Claude Code and other AI agents)

The module includes a [Model Context Protocol](https://modelcontextprotocol.io) server, so AI agents can call the tools above directly. Requires PHP 8.0+, works on Magento 2.4.x and Mage-OS, including 2.4.9.

```
bin/magento beta_dev:mcp_server [--read-only] [--timeout=300]
```

Add it to Claude Code from the Magento root (PHP on the host):

```
claude mcp add mage2-dev --scope project -- php bin/magento beta_dev:mcp_server
```

Magento in Docker — keep `-i` and never add `-t`, so the protocol stream stays clean:

```
claude mcp add mage2-dev --scope project -- docker exec -i <php-container> php /var/www/html/bin/magento beta_dev:mcp_server
```

Then ask things like *"which plugins wrap CartManagementInterface::placeOrder in the frontend?"* or *"what observers run on sales_order_place_after?"*.

See the repository's `docs/mcp.md` for the full MCP guide: every tool and its arguments, configs for other clients, testing with the MCP Inspector, and troubleshooting.

### Deploy static files (JS, CSS, HTML, JS translations, requirejs-config.js)

Before running these commands, delete the `var/view_preprocessed` folder — some static files are cached there.

```
bin/magento beta_dev:deploy_static -h
```

Deploy JS/CSS from a specific module and theme:

```
bin/magento beta_dev:deploy_static -m Magento_Checkout -f js/view/shipping-address/address-renderer/default.js -t Magento/luna
```

Deploy an adminhtml theme, or a whole directory:

```
bin/magento beta_dev:deploy_static -t Magento/backend -a adminhtml -m Magento_Catalog -f js
```

Deploy JS translations:

```
bin/magento beta_dev:deploy_static -t Magento/luna -f js-translation.json
```

Deploy `styles-m.css` / `styles-l.css`:

```
bin/magento beta_dev:deploy_static -t Magento/luna -f css/styles-l.css
bin/magento beta_dev:deploy_static -t Magento/luna -f css/styles-m.css
```

### RequireJS config

Deploy a `requirejs-config.js`:

```
bin/magento beta_dev:deploy_requirejs -t Magento/luna
```

### Support

Free and open-source. Issues and contributions welcome on the [GitHub repository](https://github.com/trunglv/mage2_dev).
