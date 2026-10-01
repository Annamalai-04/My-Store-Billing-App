package com.example.demo.service;

import com.example.demo.dto.*;
import com.example.demo.model.*;
import com.example.demo.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.*;

@Service
public class HistoryService {
	private final HistoryRepository history;
	private final ProductRepository products;

	public HistoryService(HistoryRepository h, ProductRepository p) {
		history = h;
		products = p;
	}

	@Transactional
	public String checkout(BillRequest r) {
		if (r.getItems() == null || r.getItems().isEmpty())
			throw new RuntimeException("Bill has no products");
		String bill = UUID.randomUUID().toString();
		for (BillItemRequest i : r.getItems()) {
			Product p = products.findById(i.getProductId())
					.orElseThrow(() -> new RuntimeException("Product not found"));
			if (p.getStock() < i.getQuantity())
				throw new RuntimeException("Insufficient stock for " + p.getName());
			p.setStock(p.getStock() - i.getQuantity());
			products.save(p);
			History h = new History();
			h.setBillId(bill);
			h.setCustomerId(r.getCustomerId());
			h.setWorkerId(r.getWorkerId());
			h.setProductId(i.getProductId());
			h.setQuantity(i.getQuantity());
			h.setUnitPrice(i.getUnitPrice());
			h.setDiscount(i.getDiscount());
			h.setTotalPrice(i.getTotalPrice());
			h.setSaleDate(LocalDateTime.now());
			history.save(h);
		}
		return bill;
	}

	public List<History> all() {
		return history.findAll();
	}
}