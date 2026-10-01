package com.example.demo.controller;

import com.example.demo.model.Customer;
import com.example.demo.service.CustomerService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/customers")
public class CustomerController {
	private final CustomerService s;

	public CustomerController(CustomerService s) {
		this.s = s;
	}

	@GetMapping
	public Object all() {
		return s.all();
	}

	@PostMapping("/find-or-create")
	public Customer find(@RequestBody Customer c) {
		return s.findOrCreate(c.getName(), c.getPhone());
	}
}
