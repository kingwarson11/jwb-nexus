-- Auto-generated reference schema (PostgreSQL dialect) from app/models.py
-- Generated automatically on backend startup via Base.metadata.create_all() — this file is for documentation only.

CREATE TABLE market_metrics (
	id UUID NOT NULL, 
	area VARCHAR NOT NULL, 
	category VARCHAR NOT NULL, 
	product_name VARCHAR, 
	period_start DATE NOT NULL, 
	period_end DATE NOT NULL, 
	demand_change_pct FLOAT NOT NULL, 
	participating_businesses INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
);

CREATE TABLE users (
	id UUID NOT NULL, 
	email VARCHAR NOT NULL, 
	hashed_password VARCHAR NOT NULL, 
	full_name VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
);

CREATE TABLE businesses (
	id UUID NOT NULL, 
	owner_id UUID NOT NULL, 
	name VARCHAR NOT NULL, 
	category VARCHAR, 
	area VARCHAR, 
	currency VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(owner_id) REFERENCES users (id)
);

CREATE TABLE customers (
	id UUID NOT NULL, 
	business_id UUID NOT NULL, 
	name VARCHAR, 
	phone VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(business_id) REFERENCES businesses (id)
);

CREATE TABLE expenses (
	id UUID NOT NULL, 
	business_id UUID NOT NULL, 
	category VARCHAR NOT NULL, 
	description VARCHAR, 
	amount FLOAT NOT NULL, 
	date DATE, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(business_id) REFERENCES businesses (id)
);

CREATE TABLE suppliers (
	id UUID NOT NULL, 
	business_id UUID NOT NULL, 
	name VARCHAR NOT NULL, 
	phone VARCHAR, 
	notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(business_id) REFERENCES businesses (id)
);

CREATE TABLE products (
	id UUID NOT NULL, 
	business_id UUID NOT NULL, 
	supplier_id UUID, 
	name VARCHAR NOT NULL, 
	category VARCHAR, 
	selling_price FLOAT NOT NULL, 
	cost_price FLOAT NOT NULL, 
	quantity INTEGER NOT NULL, 
	minimum_stock INTEGER NOT NULL, 
	expiry_date DATE, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(business_id) REFERENCES businesses (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id)
);

CREATE TABLE sales (
	id UUID NOT NULL, 
	business_id UUID NOT NULL, 
	customer_id UUID, 
	subtotal FLOAT NOT NULL, 
	discount FLOAT NOT NULL, 
	total FLOAT NOT NULL, 
	cost_of_goods_sold FLOAT NOT NULL, 
	status VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(business_id) REFERENCES businesses (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id)
);

CREATE TABLE inventory_movements (
	id UUID NOT NULL, 
	product_id UUID NOT NULL, 
	movement_type movementtype NOT NULL, 
	quantity_change INTEGER NOT NULL, 
	reference VARCHAR, 
	note VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE payments (
	id UUID NOT NULL, 
	sale_id UUID NOT NULL, 
	method paymentmethod NOT NULL, 
	amount FLOAT NOT NULL, 
	status paymentstatus, 
	provider_reference VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sale_id) REFERENCES sales (id)
);

CREATE TABLE sale_items (
	id UUID NOT NULL, 
	sale_id UUID NOT NULL, 
	product_id UUID NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit_price FLOAT NOT NULL, 
	unit_cost FLOAT NOT NULL, 
	line_total FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sale_id) REFERENCES sales (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

