package com.example.demo.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "customers")
public class Customer {
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long customerId;
	private String name;
	private String phone;
	private LocalDateTime createdAt, updatedAt;

	@PrePersist
	void create() {
		createdAt = updatedAt = LocalDateTime.now();
	}

	@PreUpdate
	void update() {
		updatedAt = LocalDateTime.now();
	}

	public Long getCustomerId() {
		return customerId;
	}

	public void setCustomerId(Long v) {
		customerId = v;
	}

	public String getName() {
		return name;
	}

	public void setName(String v) {
		name = v;
	}

	public String getPhone() {
		return phone;
	}

	public void setPhone(String v) {
		phone = v;
	}

	public LocalDateTime getCreatedAt() {
		return createdAt;
	}

	public LocalDateTime getUpdatedAt() {
		return updatedAt;
	}
}