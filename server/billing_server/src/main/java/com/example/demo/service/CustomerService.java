package com.example.demo.service;

import com.example.demo.model.Customer;
import com.example.demo.repository.CustomerRepository;
import org.springframework.stereotype.Service;
import java.util.*;

@Service
public class CustomerService {
	private final CustomerRepository repo;

	public CustomerService(CustomerRepository r) {
		repo = r;
	}

	public List<Customer> all() {
		return repo.findAll();
	}

	public Customer findOrCreate(String name, String phone) {
		if (phone != null && !phone.isBlank())
			return repo.findByPhone(phone).orElseGet(() -> {
				Customer c = new Customer();
				c.setName(name);
				c.setPhone(phone);
				return repo.save(c);
			});
		Customer c = new Customer();
		c.setName(name);
		return repo.save(c);
	}
}
