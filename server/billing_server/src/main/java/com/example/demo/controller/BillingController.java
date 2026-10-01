package com.example.demo.controller;

import com.example.demo.dto.BillRequest;
import com.example.demo.service.HistoryService;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/billing")
public class BillingController {
	private final HistoryService s;

	public BillingController(HistoryService s) {
		this.s = s;
	}

	@PostMapping("/checkout")
	public Object checkout(@RequestBody BillRequest r) {
		return Map.of("billId", s.checkout(r), "message", "Checkout completed");
	}
}
