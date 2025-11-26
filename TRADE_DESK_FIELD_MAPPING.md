# Trade Desk Model Field Mapping - ACTUAL SCHEMA

## Requirement Model Fields (ACTUAL)

### Foreign Keys
- `buyer_partner_id` → UUID FK to business_partners.id (NOT NULL)
- `commodity_id` → UUID FK to commodities.id (NOT NULL)
- `variety_id` → UUID FK to commodity_varieties.id (nullable)
- `created_by_user_id` → UUID FK to users.id (NOT NULL) ⚠️
- `buyer_branch_id` → UUID FK to partner_locations.id (nullable)

### Quantity Fields (Min/Max Ranges)
- `min_quantity` → Numeric(15,3) NOT NULL
- `max_quantity` → Numeric(15,3) NOT NULL
- `quantity_unit` → String(20) NOT NULL
- `preferred_quantity` → Numeric(15,3) nullable

### Quality & Budget
- `quality_requirements` → JSONB NOT NULL ⚠️
- `max_budget_per_unit` → Numeric(15,2) NOT NULL ⚠️

### Location & Payment (JSONB Arrays - not simple FK fields!)
- `delivery_locations` → JSONB nullable (array of location objects)
- `preferred_payment_terms` → JSONB nullable (array of payment term IDs)
- `preferred_delivery_terms` → JSONB nullable (array of delivery term IDs)

### ❌ FIELDS THAT DON'T EXIST:
- ~~`quantity_required`~~ → USE `min_quantity` + `max_quantity`
- ~~`unit`~~ → USE `quantity_unit`
- ~~`delivery_location_id`~~ → USE `delivery_locations` (JSONB array)
- ~~`payment_term_id`~~ → USE `preferred_payment_terms` (JSONB array)
- ~~`status`~~ → Not a direct field

---

## Availability Model Fields (ACTUAL)

### Foreign Keys
- `seller_id` → UUID FK to business_partners.id (NOT NULL) ⚠️ NOT `seller_partner_id`!
- `commodity_id` → UUID FK to commodities.id (NOT NULL)
- `location_id` → UUID FK to settings_locations.id (NOT NULL) ⚠️ NOT `pickup_location_id`!
- `seller_branch_id` → UUID FK to partner_locations.id (nullable)

### Quantity Fields
- `total_quantity` → Numeric(15,3) NOT NULL
- `available_quantity` → Numeric(15,3) NOT NULL
- `reserved_quantity` → Numeric(15,3) default 0
- `sold_quantity` → Numeric(15,3) default 0
- `min_order_quantity` → Numeric(15,3) nullable
- `quantity_unit` → String(20) nullable

### Pricing
- `price_type` → String(20) default 'FIXED' NOT NULL (FIXED/NEGOTIABLE/MATRIX)
- `base_price` → Numeric(15,2) nullable
- `price_matrix` → JSONB nullable (for MATRIX pricing)
- `currency` → String(3) default 'INR'
- `price_uom` → String(20) nullable

### Quality
- `quality_params` → JSONB nullable

### ❌ FIELDS THAT DON'T EXIST:
- ~~`seller_partner_id`~~ → USE `seller_id`
- ~~`quantity_available`~~ → USE `total_quantity` + `available_quantity` separately
- ~~`unit`~~ → USE `quantity_unit`
- ~~`price_per_unit`~~ → USE `base_price`
- ~~`pickup_location_id`~~ → USE `location_id`
- ~~`payment_term_id`~~ → Field doesn't exist at all
- ~~`status`~~ → Not a direct field

---

## Test Data Templates

### Requirement Example ✅
```python
requirement = Requirement(
    id=uuid.uuid4(),
    buyer_partner_id=buyer.id,  # ✅
    buyer_branch_id=buyer_branch.id,  # ✅ Optional
    commodity_id=seed_commodities[0].id,  # ✅
    min_quantity=Decimal("1000.00"),  # ✅
    max_quantity=Decimal("1500.00"),  # ✅
    quantity_unit="kg",  # ✅
    quality_requirements={"grade": "A"},  # ✅ JSONB NOT NULL
    max_budget_per_unit=Decimal("60.00"),  # ✅ NOT NULL
    created_by_user_id=seed_user.id,  # ✅ NOT NULL
    delivery_locations=[{"location_id": str(loc.id)}],  # ✅ JSONB array
    preferred_payment_terms=[str(payment_term.id)],  # ✅ JSONB array
)
```

### Availability Example ✅
```python
availability = Availability(
    id=uuid.uuid4(),
    seller_id=seller.id,  # ✅ NOT seller_partner_id!
    seller_branch_id=seller_branch.id,  # ✅ Optional
    commodity_id=seed_commodities[0].id,  # ✅
    location_id=seed_locations[0].id,  # ✅ NOT pickup_location_id!
    total_quantity=Decimal("2000.00"),  # ✅
    available_quantity=Decimal("2000.00"),  # ✅
    quantity_unit="kg",  # ✅
    price_type="FIXED",  # ✅ Required
    base_price=Decimal("50.00"),  # ✅ NOT price_per_unit!
    quality_params={"grade": "A"},  # ✅ JSONB
)
```
