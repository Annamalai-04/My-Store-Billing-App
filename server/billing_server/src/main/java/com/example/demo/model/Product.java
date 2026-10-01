package com.example.demo.model;

import jakarta.persistence.*;
import java.time.*;

@Entity
@Table(name = "products")
public class Product {
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long productId;
	@Column(nullable = false)
	private String name;
	@Column(name = "group_name")
	private String groupName;
	@Column(unique = true)
	private String barcode;
	private double price, discount;
	private int stock;
	private LocalDate expiryDate;
	private LocalDateTime createdAt, updatedAt;
	private String status;

	@PrePersist
	void create() {
		createdAt = updatedAt = LocalDateTime.now();
		if (status == null)
			status = "ACTIVE";
	}

	@PreUpdate
	void update() {
		updatedAt = LocalDateTime.now();
	}

	public Long getProductId() {
		return productId;
	}

	public void setProductId(Long v) {
		productId = v;
	}

	public String getName() {
		return name;
	}

	public void setName(String v) {
		name = v;
	}

	public String getGroupName() {
		return groupName;
	}

	public void setGroupName(String v) {
		groupName = v;
	}

	public String getBarcode() {
		return barcode;
	}

	public void setBarcode(String v) {
		barcode = v;
	}

	public double getPrice() {
		return price;
	}

	public void setPrice(double v) {
		price = v;
	}

	public double getDiscount() {
		return discount;
	}

	public void setDiscount(double v) {
		discount = v;
	}

	public int getStock() {
		return stock;
	}

	public void setStock(int v) {
		stock = v;
	}

	public LocalDate getExpiryDate() {
		return expiryDate;
	}

	public void setExpiryDate(LocalDate v) {
		expiryDate = v;
	}

	public LocalDateTime getCreatedAt() {
		return createdAt;
	}

	public LocalDateTime getUpdatedAt() {
		return updatedAt;
	}

	public String getStatus() {
		return status;
	}

	public void setStatus(String v) {
		status = v;
	}
}