package com.example.demo.dto;

public class BillItemRequest {
	private Long productId;
	private int quantity;
	private double unitPrice, discount, totalPrice;

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
}