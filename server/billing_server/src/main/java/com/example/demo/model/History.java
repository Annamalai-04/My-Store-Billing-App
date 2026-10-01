package com.example.demo.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "history")
public class History {
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long historyId;
	@Column(nullable = false)
	private String billId;
	private Long customerId, workerId, productId;
	private int quantity;
	private double unitPrice, discount, totalPrice;
	private LocalDateTime saleDate;

	@PrePersist
	void create() {
		if (saleDate == null)
			saleDate = LocalDateTime.now();
	}

	public Long getHistoryId() {
		return historyId;
	}

	public void setHistoryId(Long v) {
		historyId = v;
	}

	public String getBillId() {
		return billId;
	}

	public void setBillId(String v) {
		billId = v;
	}

	public Long getCustomerId() {
		return customerId;
	}

	public void setCustomerId(Long v) {
		customerId = v;
	}

	public Long getWorkerId() {
		return workerId;
	}

	public void setWorkerId(Long v) {
		workerId = v;
	}

	public Long getProductId() {
		return productId;
	}

	public void setProductId(Long v) {
		productId = v;
	}

	public int getQuantity() {
		return quantity;
	}

	public void setQuantity(int v) {
		quantity = v;
	}

	public double getUnitPrice() {
		return unitPrice;
	}

	public void setUnitPrice(double v) {
		unitPrice = v;
	}

	public double getDiscount() {
		return discount;
	}

	public void setDiscount(double v) {
		discount = v;
	}

	public double getTotalPrice() {
		return totalPrice;
	}

	public void setTotalPrice(double v) {
		totalPrice = v;
	}

	public LocalDateTime getSaleDate() {
		return saleDate;
	}

	public void setSaleDate(LocalDateTime v) {
		saleDate = v;
	}
}