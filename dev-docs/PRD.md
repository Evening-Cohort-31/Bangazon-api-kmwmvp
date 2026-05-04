<!-- Last updated: 2026-05-04 -->
<!-- Last change: Initial PRD creation -->

# Bangazon Platform API - Product Requirements Document

## Problem Statement

Bangazon is an e-commerce marketplace where users can browse and purchase products, manage their cart and orders, create stores to sell items, and track preferences like liked products and favorite sellers. The platform is a starter project provided by Nashville Software School (NSS) as part of a group backend curriculum exercise. The codebase contains working foundations alongside a set of known bugs, missing features, and untested areas that the team is responsible for completing over a 6-week sprint cycle.

## Target Users

**Shoppers:** Authenticated users who browse products, manage a cart, complete orders, and interact with other users through product recommendations and seller favorites.

**Sellers:** Authenticated users who create a store, list products for sale, and track what they have sold.

**Business Analysts:** Internal users who access HTML reports to monitor platform activity, including order status, product pricing tiers, and customer/seller relationships.

## Core Requirements

### Features

- Store list view: display store name, description, seller name, item count for sale, and a product list
- Cart management: delete all items from an open order; remove individual line items
- Product filtering: filter by minimum price and by product category
- Product recommendations: allow a user to recommend a product to another user by username
- Store profile: sellers can create a store and view products they are selling and have sold
- Product likes: users can like and unlike products; liked products appear on their profile
- Favorite sellers: users can favorite a store; favorite stores appear on their profile
- Product search: filter products by location using a query string parameter (`?location=`)
- Price filter: filter products by minimum price using a query string parameter (`?min_price=`)
- Categorized product list: show the five most recent products per category; collapse into a flat list when filters are applied

### Bug Fixes

- My Orders view displays rows but no order data
- Trash icon does not remove a line item from the cart
- Complete Order flow does not mark the order as complete
- Payment types endpoint returns all users' payment types instead of only the authenticated user's
- Payment type expiration dates are stored or returned incorrectly
- Line item DELETE endpoint does not remove the item from the cart
- Products sold count filter (`?number_sold=`) is not working
- Product and product list endpoints return a 500 ZeroDivisionError (introduced by average rating feature)
- Profile endpoint returns the wrong user regardless of auth token
- Adding a product to the cart after completing an order attaches it to the closed order instead of creating a new one
- Cart response contains a duplicate `line_items` key that needs to be removed

### Reports (HTML, Django templates)

- Favorite sellers report: list customers and their favorited sellers (`/reports/favoritesellers?customer={id}`)
- Completed orders report: order ID, customer name, total paid, payment type (`/reports/orders?status=complete`)
- Incomplete orders report: order ID, customer name, total cost of items (`/reports/orders?status=incomplete`)
- Inexpensive products report: all products priced at $999 or less (`/reports/inexpensiveproducts`)
- Expensive products report: all products priced at $1,000 or more (`/reports/expensiveproducts`)

### Tests

- Product rating: verify a rating can be added and that `avg_rating` is correct on the product response
- Product deletion: verify a deleted product no longer appears in responses
- Payment type deletion: verify a payment type can be deleted
- Cart/order integrity: verify adding a product to the cart attaches it to an open order, not a closed one
- Payment type on order: integration test for assigning a payment type to an order and verifying it persists

## Technical Stack

### Stack Decisions

- **Python / Django:** Required by NSS curriculum; provides ORM, migrations, and routing out of the box
- **Django REST Framework:** Handles serialization, viewsets, and token authentication
- **SQLite:** Default Django database; appropriate for a local development and educational context
- **Poetry:** Dependency management; a `requirements.txt` fallback is also maintained for compatibility
- **Yaak:** API client used by the team for manual request testing (replaces Postman)
- **Django Templates:** Used for HTML report endpoints; keeps reports server-rendered without requiring a separate frontend build

## Scope

### In Scope (6-sprint project)

- All feature tickets listed above (Tickets 1, 5, 6, 7, 8, 13, 14, 20, 21, 22, 23, 25, 26)
- All bug fix tickets listed above (Tickets 2, 3, 4, 27, 28, 29, 30, 31, 32, 33, 34)
- All report tickets listed above (Tickets 9, 10, 11, 12, 24)
- All test tickets listed above (Tickets 15, 16, 17, 18, 19)
- Learning spikes (Tickets 35, 36) are frontend-focused (TanStack Query, TypeScript) and apply to the client application, not this API repo

### Out of Scope

- Frontend client code (maintained in a separate repository)
- User registration flow (auth is handled via existing token system)
- Image upload or product media handling beyond what Pillow already supports
- Deployment to a production environment

## Success Criteria

- All 500-level errors are resolved and the API responds correctly to standard requests
- Authenticated users see only their own data (payment types, profile, cart)
- Cart, order, and checkout flows work end to end without side effects
- All report endpoints return correctly structured HTML
- All test tickets pass and the test suite runs without errors
- Code is reviewed and merged via pull request for each ticket

## Learning Goals

- Practice collaborating on a shared Django codebase using Git branching and pull requests
- Understand how Django REST Framework handles serializers, viewsets, and token authentication
- Build familiarity with Django's ORM for filtering, aggregation, and related data
- Learn to diagnose and fix bugs in an existing codebase by reading errors, tracing request flow, and writing targeted tests
- Write integration tests that verify end-to-end behavior rather than just unit logic
