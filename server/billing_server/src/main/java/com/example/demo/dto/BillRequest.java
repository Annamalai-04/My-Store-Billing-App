package com.example.demo.dto;

import java.util.*;

public class BillRequest {
	private Long customerId, workerId;
	private String customerPhone;
	private List<BillItemRequest> items;

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

	public String getCustomerPhone() {
		return customerPhone;
	}

	public void setCustomerPhone(String v) {
		customerPhone = v;
	}

	public List<BillItemRequest> getItems() {
		return items;
	}

	public void setItems(List<BillItemRequest> v) {
		items = v;
	}
}